from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.shortcuts import render
from accounts.models import CustomUser
from inventory.models import Category, Product, Stock, Warehouse
from procurement.models import PurchaseOrder, Supplier


@login_required
def dashboard(request):
    """Aggregates counts and low-stock alerts for the system overview."""

    low_stock_qs = (
        Stock.objects.select_related('product', 'warehouse')
        .filter(quantity__lte=F('product__reorder_level'))
    )

    context = {
        'product_count': Product.objects.count(),
        'warehouse_count': Warehouse.objects.count(),
        'stock_count': Stock.objects.count(),
        'category_count': Category.objects.count(),
        'user_count': CustomUser.objects.count(),
        'supplier_count': Supplier.objects.count(),
        'po_count': PurchaseOrder.objects.count(),
        'low_stock': low_stock_qs[:5],
        'low_stock_count': low_stock_qs.count(),
    }
    return render(request, 'dashboard.html', context)
