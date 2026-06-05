from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'phone_number')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('User Info', {
            'fields': ('first_name', 'last_name', 'phone_number', 'role')
        }),
    )
    
    list_display = ('username', 'email', 'get_full_name', 'role', 'is_staff', 'is_active')
    list_filter = UserAdmin.list_filter + ('role', 'is_active', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')
    ordering = ('-created_at',)
