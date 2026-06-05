from django import forms
from .models import Sale, Payment


class SaleForm(forms.ModelForm):
    """Savdo formasi."""
    
    class Meta:
        model = Sale
        fields = ['customer', 'product', 'seller', 'quantity', 'price_per_unit', 'discount_amount', 'payment_type', 'paid_amount', 'notes']
        widgets = {
            'customer': forms.Select(attrs={
                'class': 'form-select'
            }),
            'product': forms.Select(attrs={
                'class': 'form-select'
            }),
            'seller': forms.Select(attrs={
                'class': 'form-select',
                'required': False
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Miqdor',
                'min': '1'
            }),
            'price_per_unit': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Narx',
                'step': '0.01'
            }),
            'discount_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Chegirma',
                'step': '0.01',
                'min': '0'
            }),
            'payment_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'paid_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Avans to\'lov (nasiya uchun)',
                'step': '0.01',
                'min': '0'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Izohlar',
                'rows': 3
            }),
        }


class PaymentForm(forms.ModelForm):
    """To'lov formasi."""
    
    class Meta:
        model = Payment
        fields = ['sale', 'amount', 'payment_method', 'notes']
        widgets = {
            'sale': forms.Select(attrs={
                'class': 'form-select'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'To\'lov miqdori',
                'step': '0.01'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-select'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Izohlar',
                'rows': 3
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Faqat nasiya savdoalarni ko'rsatish
        self.fields['sale'].queryset = Sale.objects.filter(payment_type='credit')
