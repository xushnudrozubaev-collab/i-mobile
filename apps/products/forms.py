from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    """Mahsulot formasi."""
    
    class Meta:
        model = Product
        fields = [
            'brand', 'model', 'imei', 'price',
            'stock_quantity', 'warranty_months', 'description', 'is_active'
        ]
        widgets = {
            'brand': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brend (Apple, Samsung, Xiaomi...)'
            }),
            'model': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Model'
            }),
            'imei': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'IMEI raqami'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Narx',
                'step': '0.01'
            }),
            'stock_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ombordagi soni'
            }),
            'warranty_months': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Kafolat muddati (oylar)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Mahsulot haqida qo\'shimcha ma\'lumot',
                'rows': 3
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
