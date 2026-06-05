from django.shortcuts import render, redirect
import logging
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.views import LoginView as DjangoLoginView, LogoutView as DjangoLogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db.models import Q
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm


class LoginView(DjangoLoginView):
    """Foydalanuvchi kirish ko'rinishi."""
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('users:dashboard')

    def form_invalid(self, form):
        logger = logging.getLogger(__name__)
        try:
            errors = form.errors.as_json()
        except Exception:
            errors = str(form.errors)
        logger.info("Login failed for user=%s errors=%s remote=%s",
                    form.data.get('username', '<no-username>'),
                    errors,
                    self.request.META.get('REMOTE_ADDR'))
        return super().form_invalid(form)


class LogoutView(LoginRequiredMixin, DjangoLogoutView):
    """Foydalanuvchi chiqish ko'rinishi."""
    next_page = reverse_lazy('users:login')


class RegisterView(CreateView):
    """Yangi foydalanuvchi ro'yxatdan o'tkazish."""
    model = CustomUser
    template_name = 'users/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('users:login')


class DashboardView(LoginRequiredMixin, TemplateView):
    """Asosiy dashboard ko'rinishi."""
    template_name = 'users/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.sales.models import Sale
        from apps.customers.models import Customer
        
        # Bugungi savdolar
        from django.utils import timezone
        today = timezone.now().date()
        today_sales = Sale.objects.filter(date=today)
        context['today_sales_count'] = today_sales.count()
        context['today_sales_total'] = sum(s.total_price for s in today_sales) if today_sales.exists() else 0
        
        # Jami qaydlangan mijozlar
        context['total_customers'] = Customer.objects.count()
        
        # Jami foydalanuvchilar
        context['total_users'] = CustomUser.objects.count()
        
        # Bugungi yangi mijozlar
        context['new_customers_today'] = Customer.objects.filter(
            registered_date=today
        ).count()
        
        return context


class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Barcha foydalanuvchilar roʻyxati."""
    model = CustomUser
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.is_admin or self.request.user.is_staff
    
    def get_queryset(self):
        queryset = CustomUser.objects.all().order_by('-created_at')
        search = self.request.GET.get('search')
        role = self.request.GET.get('role')
        
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        
        if role:
            queryset = queryset.filter(role=role)
        
        return queryset


class UserDetailView(LoginRequiredMixin, DetailView):
    """Foydalanuvchi tafsilotlari."""
    model = CustomUser
    template_name = 'users/user_detail.html'
    context_object_name = 'user'


class UserCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Yangi foydalanuvchi yaratish."""
    model = CustomUser
    template_name = 'users/user_form.html'
    form_class = CustomUserCreationForm
    
    def test_func(self):
        return self.request.user.is_admin or self.request.user.is_staff
    
    def get_success_url(self):
        return reverse_lazy('users:user_detail', kwargs={'pk': self.object.pk})


class UserEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Foydalanuvchini tahrirlash."""
    model = CustomUser
    template_name = 'users/user_form.html'
    form_class = CustomUserChangeForm
    
    def test_func(self):
        return self.request.user.is_admin or self.request.user.is_staff or self.request.user == self.get_object()
    
    def get_success_url(self):
        return reverse_lazy('users:user_detail', kwargs={'pk': self.object.pk})


class UserDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Foydalanuvchini o'chirish."""
    model = CustomUser
    template_name = 'users/user_confirm_delete.html'
    success_url = reverse_lazy('users:user_list')
    
    def test_func(self):
        return self.request.user.is_admin or self.request.user.is_staff
