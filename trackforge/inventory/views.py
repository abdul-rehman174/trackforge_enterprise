from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from django.contrib.auth.decorators import permission_required, login_required
from django.utils.text import slugify


# --- Product Views ---
@login_required
def product_list(request):
    products = Product.objects.select_related('category').all()
    return render(request, "inventory/product_list.html", {"products": products})


@login_required
@permission_required('inventory.add_product', raise_exception=True)
def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("product_list")
    else:
        form = ProductForm()
    return render(request, "inventory/add_product.html", {"form": form})


@login_required
@permission_required('inventory.change_product', raise_exception=True)
def update_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect("product_list")
    else:
        form = ProductForm(instance=product)
    return render(request, "inventory/add_product.html", {"form": form})


@login_required
@permission_required('inventory.delete_product', raise_exception=True)
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'inventory/delete_product.html', {'product': product})


# --- Category Views ---
@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, "category/category_list.html", {"categories": categories})


@login_required
@permission_required('inventory.add_category', raise_exception=True)
def category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.slug = slugify(category.name)
            category.save()
            return redirect("category_list")
    else:
        form = CategoryForm()
    return render(request, "category/category_form.html", {"form": form, "title": "Add Category"})


@login_required
@permission_required('inventory.change_category', raise_exception=True)
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save(commit=False)
            category.slug = slugify(category.name)
            category.save()
            return redirect("category_list")
    else:
        form = CategoryForm(instance=category)
    return render(request, "category/category_form.html", {"form": form, "title": "Edit Category"})


@login_required
@permission_required('inventory.delete_category', raise_exception=True)
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        category.delete()
        return redirect("category_list")
    return render(request, "category/delete_category.html", {"category": category})


# --- Warehouse Views ---
@login_required
def warehouse_list(request):
    warehouses = Warehouse.objects.all()
    return render(request, "warehouse/warehouse_list.html", {"warehouses": warehouses})


@login_required
@permission_required('inventory.add_warehouse', raise_exception=True)
def warehouse_create(request):
    if request.method == "POST":
        form = WarehouseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("warehouse_list")
    else:
        form = WarehouseForm()
    return render(request, "warehouse/warehouse_form.html", {"form": form, "title": "Add Warehouse"})


@login_required
@permission_required('inventory.change_warehouse', raise_exception=True)
def warehouse_update(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    if request.method == "POST":
        form = WarehouseForm(request.POST, instance=warehouse)
        if form.is_valid():
            form.save()
            return redirect("warehouse_list")
    else:
        form = WarehouseForm(instance=warehouse)
    return render(request, "warehouse/warehouse_form.html", {"form": form, "title": "Edit Warehouse"})


@login_required
@permission_required('inventory.delete_warehouse', raise_exception=True)
def warehouse_delete(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    if request.method == "POST":
        warehouse.delete()
        return redirect("warehouse_list")
    return render(request, "warehouse/delete_warehouse.html", {"warehouse": warehouse})


# --- Stock View ---
@login_required
def stock_list(request):
    stock = Stock.objects.select_related('product', 'warehouse').all()
    return render(request, "inventory/stock_list.html", {"stock": stock})


# --- StockTransaction View ---
@login_required
def transaction_history(request):
    transactions = StockTransaction.objects.select_related(
        'stock__product',
        'stock__warehouse'
    ).order_by('-created_at')

    return render(request, "inventory/transaction_list.html", {"transactions": transactions})
