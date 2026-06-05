from django.contrib import admin
from .models import Sale, Payment


class PaymentInline(admin.TabularInline):
    """To'lovlar uchun inline admin."""
    model = Payment
    extra = 1
    fields = ('payment_date', 'amount', 'payment_method', 'notes')


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('customer', 'product', 'seller', 'date', 'total_price', 'payment_type', 'is_completed')
    list_filter = ('payment_type', 'is_completed', 'date')
    search_fields = ('customer__first_name', 'customer__last_name', 'product__brand', 'product__model')
    readonly_fields = ('date', 'created_at', 'updated_at', 'total_price')
    inlines = [PaymentInline]
    
    fieldsets = (
        ('Savdo ma\'lumotlari', {
            'fields': ('customer', 'product', 'seller', 'date')
        }),
        ('Miqdor va narx', {
            'fields': ('quantity', 'price_per_unit', 'total_price')
        }),
        ('To\'lov', {
            'fields': ('payment_type', 'paid_amount', 'is_completed')
        }),
        ('Qo\'shimcha', {
            'fields': ('notes',)
        }),
        ('Tizim ma\'lumotlari', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ('-date',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('sale', 'amount', 'payment_date', 'payment_method', 'created_by')
    list_filter = ('payment_method', 'payment_date')
    search_fields = ('sale__customer__first_name', 'sale__customer__last_name')
    readonly_fields = ('payment_date', 'created_at', 'created_by')
    
    fieldsets = (
        ('To\'lov ma\'lumotlari', {
            'fields': ('sale', 'amount', 'payment_date', 'payment_method')
        }),
        ('Qo\'shimcha', {
            'fields': ('notes', 'created_by')
        }),
        ('Tizim ma\'lumotlari', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ('-payment_date',)
    
    def save_model(self, request, obj, form, change):
        """To'lov kim qo'shayotganini saqlab qo'yish."""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
