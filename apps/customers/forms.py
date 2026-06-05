from django import forms
from .models import Customer


class CustomerForm(forms.ModelForm):
    """Mijoz formasi."""
    
    class Meta:
        model = Customer
        fields = [
            'first_name', 'last_name', 'middle_name',
            'phone_number', 'email', 'address',
            'passport_number', 'passport_issued_date', 'passport_issued_by'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ismi'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Familyasi'
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Otasining ismi'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+998901234567'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'example@email.com'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'To\'liq manzil',
                'rows': 3
            }),
            'passport_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Pasport raqami'
            }),
            'passport_issued_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'passport_issued_by': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Pasport bergan organ'
            }),
        }
