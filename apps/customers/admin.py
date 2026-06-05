from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone_number', 'email', 'registered_date', 'is_active')
    list_filter = ('is_active', 'registered_date')
    search_fields = ('first_name', 'last_name', 'phone_number', 'email', 'passport_number')
    readonly_fields = ('registered_date', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Shaxsiy ma\'lumotlar', {
            'fields': ('first_name', 'last_name', 'middle_name')
        }),
        ('Kontakt ma\'lumotlari', {
            'fields': ('phone_number', 'email', 'address')
        }),
        ('Pasport ma\'lumotlari', {
            'fields': ('passport_number', 'passport_issued_date', 'passport_issued_by')
        }),
        ('Tizim ma\'lumotlari', {
            'fields': ('is_active', 'registered_date', 'created_at', 'updated_at')
        }),
    )
    
    add_fieldsets = (
        ('Shaxsiy ma\'lumotlar', {
            'fields': ('first_name', 'last_name', 'middle_name')
        }),
        ('Kontakt ma\'lumotlari', {
            'fields': ('phone_number', 'email', 'address')
        }),
        ('Pasport ma\'lumotlari', {
            'fields': ('passport_number', 'passport_issued_date', 'passport_issued_by')
        }),
    )
    
    ordering = ('-registered_date',)
