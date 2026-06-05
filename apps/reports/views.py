from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import json

from apps.sales.models import Sale, Payment
from apps.customers.models import Customer
from apps.products.models import Product


class SalesReportView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Savdo hisoboti."""
    template_name = 'reports/sales_report.html'
    
    def test_func(self):
        return self.request.user.is_admin or self.request.user.is_manager
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Bugungi savdolar
        today = timezone.now().date()
        today_sales = Sale.objects.filter(date=today)
        context['today_sales_count'] = today_sales.count()
        context['today_sales_total'] = today_sales.aggregate(Sum('total_price')).get('total_price__sum') or Decimal('0')
        
        # Bu oyning savdolari
        first_day_of_month = today.replace(day=1)
        month_sales = Sale.objects.filter(date__gte=first_day_of_month)
        context['month_sales_count'] = month_sales.count()
        context['month_sales_total'] = month_sales.aggregate(Sum('total_price')).get('total_price__sum') or Decimal('0')
        
        # O'tgan 7 kunning savdolari (Grafik uchun)
        last_7_days_sales = []
        labels = []
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            sales_sum = Sale.objects.filter(date=date).aggregate(Sum('total_price')).get('total_price__sum') or 0
            last_7_days_sales.append(float(sales_sum))
            labels.append(date.strftime('%Y-%m-%d'))
        
        context['chart_sales_labels'] = json.dumps(labels)
        context['chart_sales_data'] = json.dumps(last_7_days_sales)
        
        # To'lov turi bo'yicha tahlil
        payment_type_analysis = Sale.objects.values('payment_type').annotate(count=Count('id'), total=Sum('total_price'))
        context['payment_type_analysis'] = payment_type_analysis
        
        return context


class DebtorsReportView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Qarzdor mijozlar hisoboti."""
    template_name = 'reports/debtors_report.html'
    
    def test_func(self):
        return self.request.user.is_admin or self.request.user.is_manager
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Nasiya savdolar va to'lovlari
        credit_sales = Sale.objects.filter(payment_type='credit')
        
        # Har bir mijozni tekshirish
        debtors = []
        total_debt = Decimal('0')
        
        for sale in credit_sales:
            total_paid = sale.payments.aggregate(Sum('amount')).get('amount__sum') or Decimal('0')
            remaining = sale.total_price - total_paid
            
            if remaining > 0:
                debtors.append({
                    'customer': sale.customer,
                    'sale': sale,
                    'total_debt': remaining,
                    'paid': total_paid,
                    'sale_amount': sale.total_price
                })
                total_debt += remaining
        
        context['debtors'] = debtors
        context['total_debt'] = total_debt
        context['debtors_count'] = len(debtors)
        # calculate average debt per debtor (avoid division by zero)
        if context['debtors_count'] > 0:
            context['average_debt'] = total_debt / context['debtors_count']
        else:
            context['average_debt'] = Decimal('0')
        
        return context


class ProductSalesReportView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Mahsulot sotuvlari hisoboti."""
    template_name = 'reports/product_sales_report.html'
    
    def test_func(self):
        return self.request.user.is_admin or self.request.user.is_manager
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Eng ko'p sotilgan mahsulotlar
        top_products_qs = Sale.objects.values('product').annotate(
            count=Count('id'),
            total=Sum('total_price'),
            qty=Sum('quantity'),
        ).order_by('-count')[:10]
        
        top_products = []
        product_labels = []
        product_quantities = []

        for item in top_products_qs:
            try:
                product = Product.objects.get(id=item['product'])
            except Product.DoesNotExist:
                continue
            qty_sold = item['qty'] or item['count']
            total_rev = item['total'] or Decimal('0')
            avg_price = total_rev / qty_sold if qty_sold else Decimal('0')

            top_products.append({
                'product':       product,
                'display_name':  product.display_name,
                'brand':         product.brand,
                'quantity_sold': qty_sold,
                'total_revenue': total_rev,
                'avg_price':     avg_price,
            })
            product_labels.append(f"{product.brand} {product.model}")
            product_quantities.append(int(qty_sold))

        context['top_products']        = top_products
        context['product_labels']      = json.dumps(product_labels)
        context['product_quantities']  = json.dumps(product_quantities)
        
        return context


class InventoryReportView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Ombor holati hisoboti."""
    template_name = 'reports/inventory_report.html'
    
    def test_func(self):
        return self.request.user.is_warehouse_manager or self.request.user.is_admin or self.request.user.is_manager
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        all_products = Product.objects.all().order_by('brand', 'model')
        
        total_inventory_value = Decimal('0')
        total_quantity = 0
        low_stock_products = []
        products_with_value = []

        for product in all_products:
            inv_value = product.price * product.stock_quantity
            total_inventory_value += inv_value
            total_quantity += product.stock_quantity
            # annotate inventory_value onto the object for template use
            product.inventory_value = inv_value
            products_with_value.append(product)
            if 0 < product.stock_quantity <= 5:
                low_stock_products.append(product)

        context['products']             = products_with_value
        context['total_products']       = all_products.count()
        context['total_quantity']       = total_quantity
        context['inventory_value']      = total_inventory_value
        context['low_stock_count']      = len(low_stock_products)
        context['low_stock_products']   = low_stock_products
        context['out_of_stock_products'] = [p for p in products_with_value if p.stock_quantity == 0]
        
        return context


class SellerPerformanceView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Sotuvchilarning ishlash natijasi."""
    template_name = 'reports/seller_performance.html'
    
    def test_func(self):
        return self.request.user.is_admin or self.request.user.is_manager
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        from apps.users.models import CustomUser
        sellers = CustomUser.objects.filter(role='seller')
        
        seller_list = []
        seller_names = []
        seller_amounts = []

        for seller in sellers:
            sales = Sale.objects.filter(seller=seller)
            count = sales.count()
            total_amount = sales.aggregate(t=Sum('total_price')).get('t') or Decimal('0')
            paid_amount  = sales.aggregate(t=Sum('paid_amount')).get('t') or Decimal('0')
            credit_amount = total_amount - paid_amount
            avg_sale = total_amount / count if count > 0 else Decimal('0')

            seller_list.append({
                'seller': seller,
                'get_full_name': seller.get_full_name() or seller.username,
                'total_sales': count,
                'total_amount': total_amount,
                'avg_sale': avg_sale,
                'paid_sales': paid_amount,
                'credit_amount': credit_amount,
            })
            seller_names.append(seller.get_full_name() or seller.username)
            seller_amounts.append(float(total_amount))

        # Ko'p sotgan birinchi
        seller_list.sort(key=lambda x: x['total_amount'], reverse=True)

        context['sellers'] = seller_list
        context['seller_names'] = json.dumps(seller_names)
        context['seller_amounts'] = json.dumps(seller_amounts)
        
        return context


class FinancialReportView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Moliyaviy hisoboti."""
    template_name = 'reports/financial_report.html'
    
    def test_func(self):
        return self.request.user.is_admin or self.request.user.is_manager
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Jami savdo
        total_sales = Sale.objects.aggregate(Sum('total_price')).get('total_price__sum') or Decimal('0')
        
        # Jami to'lovlangan
        total_payments = Payment.objects.aggregate(Sum('amount')).get('amount__sum') or Decimal('0')
        
        # Jami qarz
        total_debt = total_sales - total_payments
        
        # Naqd to'lovlar
        cash_sales = Sale.objects.filter(payment_type='cash').aggregate(Sum('total_price')).get('total_price__sum') or Decimal('0')
        
        # Karta to'lovlari
        card_sales = Sale.objects.filter(payment_type='card').aggregate(Sum('total_price')).get('total_price__sum') or Decimal('0')
        
        # Nasiya
        credit_sales_total = Sale.objects.filter(payment_type='credit').aggregate(Sum('total_price')).get('total_price__sum') or Decimal('0')
        
        context['total_sales'] = total_sales
        context['total_payments'] = total_payments
        context['total_debt'] = total_debt
        context['cash_sales'] = cash_sales
        context['card_sales'] = card_sales
        context['credit_sales_total'] = credit_sales_total
        
        # Grafik uchun
        labels = ['Naqd', 'Karta', 'Nasiya']
        data = [float(cash_sales), float(card_sales), float(credit_sales_total)]
        
        context['chart_payment_type_labels'] = json.dumps(labels)
        context['chart_payment_type_data'] = json.dumps(data)
        
        return context
