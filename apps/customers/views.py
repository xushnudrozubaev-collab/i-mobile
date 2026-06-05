from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db.models import Q, Sum
from .models import Customer
from .forms import CustomerForm


class CustomerListView(LoginRequiredMixin, ListView):
    """Barcha mijozlar roʻyxati."""
    model = Customer
    template_name = 'customers/customer_list.html'
    context_object_name = 'customers'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Customer.objects.all().order_by('-registered_date')
        search = self.request.GET.get('search')
        
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(phone_number__icontains=search) |
                Q(email__icontains=search)
            )
        
        return queryset


class CustomerDetailView(LoginRequiredMixin, DetailView):
    """Mijoz tafsilotlari."""
    model = Customer
    template_name = 'customers/customer_detail.html'
    context_object_name = 'customer'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Mijozning savdolari
        context['sales'] = self.object.sale_set.all().order_by('-date')
        # Miroj qarzlar
        context['credit_sales'] = self.object.sale_set.filter(payment_type='credit')
        return context


class CustomerCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Yangi mijoz qo'shish."""
    model = Customer
    template_name = 'customers/customer_form.html'
    form_class = CustomerForm
    
    def test_func(self):
        return self.request.user.is_seller or self.request.user.is_manager or self.request.user.is_admin
    
    def get_success_url(self):
        return reverse_lazy('customers:customer_detail', kwargs={'pk': self.object.pk})


class CustomerEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Mijozni tahrirlash."""
    model = Customer
    template_name = 'customers/customer_form.html'
    form_class = CustomerForm
    
    def test_func(self):
        return self.request.user.is_seller or self.request.user.is_manager or self.request.user.is_admin
    
    def get_success_url(self):
        return reverse_lazy('customers:customer_detail', kwargs={'pk': self.object.pk})


class CustomerDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Mijozni o'chirish."""
    model = Customer
    template_name = 'customers/customer_confirm_delete.html'
    success_url = reverse_lazy('customers:customer_list')
    
    def test_func(self):
        return self.request.user.is_manager or self.request.user.is_admin


class DiscountCustomerListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Chegirma olgan mijozlar ro'yxati."""
    model = Customer
    template_name = 'customers/discounted_list.html'
    context_object_name = 'customers'
    paginate_by = 20

    def test_func(self):
        # allow sellers, managers and admins to view
        return self.request.user.is_seller or self.request.user.is_manager or self.request.user.is_admin

    def get_queryset(self):
        qs = Customer.objects.filter(
            sale__discount_amount__gt=0
        ).annotate(
            total_discount=Sum('sale__discount_amount', filter=Q(sale__discount_amount__gt=0))
        ).distinct()
        return qs
