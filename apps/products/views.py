from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Product
from .forms import ProductForm


class ProductListView(LoginRequiredMixin, ListView):
    """Barcha mahsulotlar ro'yxati."""
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Product.objects.all().order_by('-created_at')
        search = self.request.GET.get('search')
        brand = self.request.GET.get('brand')
        in_stock = self.request.GET.get('in_stock')
        
        if search:
            queryset = queryset.filter(
                Q(brand__icontains=search) |
                Q(model__icontains=search) |
                Q(imei__icontains=search)
            )
        
        if brand:
            queryset = queryset.filter(brand__iexact=brand)
        
        if in_stock == 'on':
            queryset = queryset.filter(stock_quantity__gt=0)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brands'] = Product.objects.values_list('brand', flat=True).distinct()
        return context


class ProductDetailView(LoginRequiredMixin, DetailView):
    """Mahsulot tafsilotlari."""
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'


class ProductCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Yangi mahsulot qo'shish."""
    model = Product
    template_name = 'products/product_form.html'
    form_class = ProductForm
    
    def test_func(self):
        return self.request.user.is_warehouse_manager or self.request.user.is_manager or self.request.user.is_admin
    
    def get_success_url(self):
        return reverse_lazy('products:product_detail', kwargs={'pk': self.object.pk})


class ProductEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Mahsulotni tahrirlash."""
    model = Product
    template_name = 'products/product_form.html'
    form_class = ProductForm
    
    def test_func(self):
        return self.request.user.is_warehouse_manager or self.request.user.is_manager or self.request.user.is_admin
    
    def get_success_url(self):
        return reverse_lazy('products:product_detail', kwargs={'pk': self.object.pk})


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Mahsulotni o'chirish."""
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('products:product_list')
    
    def test_func(self):
        return self.request.user.is_manager or self.request.user.is_admin
