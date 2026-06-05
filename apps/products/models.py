from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from decimal import Decimal


class Product(models.Model):
    """Telefon mahsulotlari."""
    
    # Brend va model
    brand = models.CharField(
        max_length=100,
        verbose_name=_('Brend'),
        db_index=True
    )
    model = models.CharField(
        max_length=100,
        verbose_name=_('Model'),
        db_index=True
    )
    
    # Unikal IMEI
    imei = models.CharField(
        max_length=15,
        unique=True,
        verbose_name=_('IMEI'),
        db_index=True
    )
    
    # Narx va ombor
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name=_('Narx')
    )
    stock_quantity = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('Ombordagi soni')
    )
    
    # Kafolat
    warranty_months = models.IntegerField(
        default=12,
        validators=[MinValueValidator(0)],
        verbose_name=_('Kafolat muddati (oylar)')
    )
    
    # Qo'shimcha
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Ta\'rif')
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
        verbose_name = _('Mahsulot')
        verbose_name_plural = _('Mahsulotlar')
        ordering = ['-created_at']
        unique_together = ('brand', 'model', 'imei')
        indexes = [
            models.Index(fields=['brand']),
            models.Index(fields=['model']),
            models.Index(fields=['imei']),
            models.Index(fields=['stock_quantity']),
        ]
    
    def __str__(self):
        return f"{self.brand} {self.model} ({self.imei})"
    
    @property
    def display_name(self):
        """Ko'rsatish uchun name."""
        return f"{self.brand} {self.model}"
    
    def is_in_stock(self):
        """Ombordan bor-yo'qligini tekshirish."""
        return self.stock_quantity > 0
    
    def decrease_stock(self, quantity):
        """Ombordan kamaytirish."""
        if self.stock_quantity >= quantity:
            self.stock_quantity -= quantity
            self.save()
            return True
        return False
    
    def increase_stock(self, quantity):
        """Omborga qo'shish."""
        self.stock_quantity += quantity
        self.save()
