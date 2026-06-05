from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db.models import Q, Sum
from django.utils import timezone
from .models import Sale, Payment
from .forms import SaleForm, PaymentForm


class SaleListView(LoginRequiredMixin, ListView):
    """Barcha savdolar ro'yxati."""
    model = Sale
    template_name = 'sales/sale_list.html'
    context_object_name = 'sales'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Sale.objects.all().order_by('-date')
        search = self.request.GET.get('search')
        payment_type = self.request.GET.get('payment_type')
        status = self.request.GET.get('status')
        
        if search:
            queryset = queryset.filter(
                Q(customer__first_name__icontains=search) |
                Q(customer__last_name__icontains=search) |
                Q(product__brand__icontains=search) |
                Q(product__model__icontains=search)
            )
        
        if payment_type:
            queryset = queryset.filter(payment_type=payment_type)
        
        if status == 'completed':
            queryset = queryset.filter(is_completed=True)
        elif status == 'pending':
            queryset = queryset.filter(is_completed=False)
        
        return queryset


class SaleDetailView(LoginRequiredMixin, DetailView):
    """Savdo tafsilotlari."""
    model = Sale
    template_name = 'sales/sale_detail.html'
    context_object_name = 'sale'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payments'] = self.object.payments.all()
        return context


class SaleCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Yangi savdo qo'shish."""
    model = Sale
    template_name = 'sales/sale_form.html'
    form_class = SaleForm
    
    def test_func(self):
        return self.request.user.is_seller or self.request.user.is_admin
    
    def form_valid(self, form):
        # Sotuvchini avtomatik qo'yish
        form.instance.seller = self.request.user
        sale = form.save(commit=False)
        # Naqd/karta bo'lsa to'liq to'langan
        base = sale.price_per_unit * sale.quantity
        discount = sale.discount_amount or 0
        from decimal import Decimal
        sale.total_price = max(base - discount, Decimal('0'))
        if sale.payment_type in ('cash', 'card'):
            sale.paid_amount = sale.total_price
            sale.is_completed = True
        else:
            # Nasiya: faqat form da paid_amount kiritilgan bo'lsa
            if not sale.paid_amount:
                sale.paid_amount = Decimal('0')
            sale.is_completed = (sale.paid_amount >= sale.total_price)
        sale.save()
        self.object = sale
        from django.urls import reverse
        return redirect(self.get_success_url())
    
    def get_success_url(self):
        return reverse_lazy('sales:sale_detail', kwargs={'pk': self.object.pk})


class SaleEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Savdoni tahrirlash."""
    model = Sale
    template_name = 'sales/sale_form.html'
    form_class = SaleForm
    
    def test_func(self):
        return self.request.user.is_admin or self.request.user == self.get_object().seller
    
    def get_success_url(self):
        return reverse_lazy('sales:sale_detail', kwargs={'pk': self.object.pk})


class SaleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Savdoni o'chirish."""
    model = Sale
    template_name = 'sales/sale_confirm_delete.html'
    success_url = reverse_lazy('sales:sale_list')
    
    def test_func(self):
        return self.request.user.is_admin


class CreditSaleListView(LoginRequiredMixin, ListView):
    """Nasiya savdolar ro'yxati."""
    model = Sale
    template_name = 'sales/credit_sale_list.html'
    context_object_name = 'sales'
    paginate_by = 20
    
    def get_queryset(self):
        return Sale.objects.filter(payment_type='credit').order_by('-date')


class PaymentListView(LoginRequiredMixin, ListView):
    """Barcha to'lovlar ro'yxati."""
    model = Payment
    template_name = 'sales/payment_list.html'
    context_object_name = 'payments'
    paginate_by = 20
    
    def get_queryset(self):
        search = self.request.GET.get('search')
        queryset = Payment.objects.all().order_by('-payment_date')
        
        if search:
            queryset = queryset.filter(
                Q(sale__customer__first_name__icontains=search) |
                Q(sale__customer__last_name__icontains=search)
            )
        
        return queryset


class PaymentCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Yangi to'lov qo'shish."""
    model = Payment
    template_name = 'sales/payment_form.html'
    form_class = PaymentForm
    
    def test_func(self):
        return self.request.user.is_manager or self.request.user.is_admin
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('sales:sale_detail', kwargs={'pk': self.object.sale.pk})


class PaymentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """To'lovni o'chirish."""
    model = Payment
    template_name = 'sales/payment_confirm_delete.html'
    
    def test_func(self):
        return self.request.user.is_admin
    
    def get_success_url(self):
        sale_pk = self.object.sale.pk
        return reverse_lazy('sales:sale_detail', kwargs={'pk': sale_pk})
    
    def delete(self, request, *args, **kwargs):
        """To'lovni o'chirishda sale dagi to'lov summasi qaytarish."""
        payment = self.get_object()
        sale = payment.sale
        sale.paid_amount -= payment.amount
        sale.is_completed = False
        sale.save()
        return super().delete(request, *args, **kwargs)
