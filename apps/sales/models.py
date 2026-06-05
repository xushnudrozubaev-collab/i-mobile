from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from apps.customers.models import Customer
from apps.products.models import Product
from apps.users.models import CustomUser


class Sale(models.Model):
    """Savdo tranzaksiyalari."""
    
    PAYMENT_TYPE_CHOICES = (
        ('cash', _('Naqd pul')),
        ('card', _('Karta')),
        ('credit', _('Nasiya')),
    )
    
    # Bog'langanliklar
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        verbose_name=_('Mijoz')
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name=_('Mahsulot')
    )
    seller = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('Sotuvchi'),
        limit_choices_to={'role': 'seller'}
    )
    
    # Savdo ma'lumotlari
    date = models.DateField(
        auto_now_add=True,
        verbose_name=_('Sana'),
        db_index=True
    )
    quantity = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name=_('Qadri')
    )
    price_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name=_('Bitta mahsulot narxi')
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name=_('Chegirma summasi')
    )
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name=_('Umumiy narx')
    )
    
    # To'lov ma'lumotlari
    payment_type = models.CharField(
        max_length=10,
        choices=PAYMENT_TYPE_CHOICES,
        default='cash',
        verbose_name=_('To\'lov turi')
    )
    paid_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name=_('To\'langan summa')
    )
    
    # Qo'shimcha
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Izohlar')
    )
    is_completed = models.BooleanField(
        default=True,
        verbose_name=_('To\'liq to\'langan')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Yaratilgan sana')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('O\'zgartirilgan sana')
    )
    
    class Meta:
        verbose_name = _('Savdo')
        verbose_name_plural = _('Savdolar')
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['customer']),
            models.Index(fields=['payment_type']),
        ]
    
    def __str__(self):
        return f"{self.customer.full_name} - {self.product.display_name} ({self.date})"
    
    def save(self, *args, **kwargs):
        """Saqlash vaqtida ombordagi miqdorni kamaytirish."""
        # Yangi savdo bo'lsa, ombordagi miqdorni kamaytir
        if not self.pk:
            self.product.decrease_stock(self.quantity)
        
        # Total narxni hisoblash (chegirma inobatga olinadi)
        if not self.total_price:
            base = self.price_per_unit * self.quantity
            self.total_price = max(base - self.discount_amount, Decimal('0.00'))
        
        super().save(*args, **kwargs)
    
    @property
    def remaining_amount(self):
        """Qolgan to'lash kerak bo'lgan summa."""
        return max(self.total_price - self.paid_amount, Decimal('0'))
    
    @property
    def is_credit_sale(self):
        """Nasiya savdosi bo'lsa."""
        return self.payment_type == 'credit'


class Payment(models.Model):
    """Nasiya savdolar uchun to'lovlar."""
    
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_('Savdo'),
        limit_choices_to={'payment_type': 'credit'}
    )
    
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name=_('To\'lov miqdori')
    )
    payment_date = models.DateField(
        auto_now_add=True,
        verbose_name=_('To\'lov sanasi'),
        db_index=True
    )
    payment_method = models.CharField(
        max_length=20,
        choices=[
            ('cash', _('Naqd pul')),
            ('card', _('Karta')),
            ('transfer', _('O\'tkazma')),
        ],
        default='cash',
        verbose_name=_('To\'lov usuli')
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Izohlar')
    )
    
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('Kiritgan shaxs')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Yaratilgan sana')
    )
    
    class Meta:
        verbose_name = _('To\'lov')
        verbose_name_plural = _('To\'lovlar')
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['payment_date']),
            models.Index(fields=['sale']),
        ]
    
    def __str__(self):
        return f"{self.sale.customer.full_name} - {self.amount} ({self.payment_date})"
    
    def save(self, *args, **kwargs):
        """To'lov saqlashda sale ga to'lov summasi qo'shish."""
        super().save(*args, **kwargs)
        
        # Sale ni tahrir qilish
        self.sale.paid_amount = self.sale.paid_amount + self.amount
        if self.sale.paid_amount >= self.sale.total_price:
            self.sale.is_completed = True
        else:
            self.sale.is_completed = False
        self.sale.save()
