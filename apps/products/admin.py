from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'imei', 'price', 'stock_quantity', 'is_active', 'created_at')
    list_filter = ('brand', 'is_active', 'created_at')
    search_fields = ('brand', 'model', 'imei')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Mahsulot ma\'lumotlari', {
            'fields': ('brand', 'model', 'imei')
        }),
        ('Narx va ombor', {
            'fields': ('price', 'stock_quantity')
        }),
        ('Qo\'shimcha', {
            'fields': ('warranty_months', 'description', 'is_active')
        }),
        ('Tizim ma\'lumotlari', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ('-created_at',)
