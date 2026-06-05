from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    # Savdolar
    path('', views.SaleListView.as_view(), name='sale_list'),
    path('create/', views.SaleCreateView.as_view(), name='sale_create'),
    path('<int:pk>/', views.SaleDetailView.as_view(), name='sale_detail'),
    path('<int:pk>/edit/', views.SaleEditView.as_view(), name='sale_edit'),
    path('<int:pk>/delete/', views.SaleDeleteView.as_view(), name='sale_delete'),
    
    # Nasiya savdolar
    path('credit/', views.CreditSaleListView.as_view(), name='credit_sale_list'),
    
    # To'lovlar
    path('payments/', views.PaymentListView.as_view(), name='payment_list'),
    path('payments/create/', views.PaymentCreateView.as_view(), name='payment_create'),
    path('payments/<int:pk>/delete/', views.PaymentDeleteView.as_view(), name='payment_delete'),
]
