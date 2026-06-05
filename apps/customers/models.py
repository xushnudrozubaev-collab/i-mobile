from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from decimal import Decimal

class Customer(models.Model):
    """Kompaniya mijozlari."""
    
    # Shaxsiy ma'lumotlar
    first_name = models.CharField(
        max_length=100,
        verbose_name=_('Ismi')
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name=_('Familyasi')
    )
    middle_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Otasining ismi')
    )
    
    # Kontakt ma'lumotlari
    phone_number = models.CharField(
        max_length=20,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\+?998\d{9}$',
                message='Telefon raqami +998XXXXXXXXX formatida bo\'lishi kerak',
            )
        ],
        verbose_name=_('Telefon raqami')
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name=_('Email')
    )
    
    # Manzil ma'lumotlari
    address = models.TextField(
        verbose_name=_('Manzil')
    )
    
    # Pasport ma'lumotlari
    passport_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('Pasport raqami')
    )
    passport_issued_date = models.DateField(
        verbose_name=_('Pasport berilgan sana')
    )
    passport_issued_by = models.CharField(
        max_length=200,
        verbose_name=_('Pasport bergan organ')
    )
    
    # Administrative
    registered_date = models.DateField(
        auto_now_add=True,
        verbose_name=_('Ro\'yxatdan o\'tgan sana')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Faol')
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
        verbose_name = _('Mijoz')
        verbose_name_plural = _('Mijozlar')
        ordering = ['-registered_date']
        indexes = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['passport_number']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.phone_number})"
    
    @property
    def full_name(self):
        """To'liq ism."""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    @property
    def total_debt(self):
        """Jami qarz."""
        from apps.sales.models import Sale, Payment
        
        # Barcha nasiya savdolarning jami summasini olish
        credit_sales = Sale.objects.filter(
            customer=self,
            payment_type='credit'
        ).values_list('id', flat=True)
        
        total_sale_amount = Sum('total_price')
        total_from_sales = Sale.objects.filter(id__in=credit_sales).aggregate(total=total_sale_amount).get('total') or Decimal('0')
        
        # Barcha to'lovlarni qayta hisoblab olish
        total_payments = Payment.objects.filter(
            sale__in=credit_sales
        ).aggregate(total=models.Sum('amount')).get('total') or Decimal('0')
        
        return max(total_from_sales - total_payments, Decimal('0'))


# Import Sum for aggregation
from django.db.models import Sum
