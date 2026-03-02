from django.shortcuts import render
from django.contrib.auth import get_user_model
from inventory.models import Product, Warehouse, Stock, Category
from accounts.models import CustomUser
from procurement.models import Supplier, PurchaseOrder




def dashboard(request):
    """
    Main hub view that aggregates counts for the system overview.
    """
    context = {
        'product_count': Product.objects.count(),
        'warehouse_count': Warehouse.objects.count(),
        'stock_count': Stock.objects.count(),
        'category_count': Category.objects.count(),
        'user_count': CustomUser.objects.count(),
        'supplier_count': Supplier.objects.count(),
        'po_count':PurchaseOrder.objects.count()

    }
    return render(request, 'dashboard.html', context)