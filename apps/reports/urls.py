from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('sales/', views.SalesReportView.as_view(), name='sales_report'),
    path('debtors/', views.DebtorsReportView.as_view(), name='debtors_report'),
    path('products/', views.ProductSalesReportView.as_view(), name='product_sales_report'),
    path('inventory/', views.InventoryReportView.as_view(), name='inventory_report'),
    path('sellers/', views.SellerPerformanceView.as_view(), name='seller_performance'),
    path('financial/', views.FinancialReportView.as_view(), name='financial_report'),
]
