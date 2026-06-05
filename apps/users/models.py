from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    """Custom User model for i-Mobile CRM with role-based access control."""
    
    ROLE_CHOICES = (
        ('admin', _('Administrator')),
        ('seller', _('Sotuvchi (Seller)')),
        ('warehouse', _('Omborchi (Warehouse Manager)')),
        ('manager', _('Menejer (Manager)')),
    )
    
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('Telefon raqami')
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='seller',
        verbose_name=_('Rol')
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
        verbose_name = _('Foydalanuvchi')
        verbose_name_plural = _('Foydalanuvchilar')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser
    
    @property
    def is_seller(self):
        return self.role == 'seller'
    
    @property
    def is_warehouse_manager(self):
        return self.role == 'warehouse'
    
    @property
    def is_manager(self):
        return self.role == 'manager'
