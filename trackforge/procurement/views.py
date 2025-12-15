from django.contrib.auth.decorators import login_required,permission_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Supplier, PurchaseOrder
from .forms import SupplierForm, PurchaseOrderForm

# Supplier Views

@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, 'supplier_list.html', {'suppliers': suppliers})


@permission_required('procurement.add_supplier',raise_exception=True)
def add_supplier(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('supplier_list')
    else:
        form = SupplierForm()
    return render(request, 'add_supplier.html', {'form': form})


@permission_required('procurement.change_supplier',raise_exception=True)
def update_supplier(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            return redirect('supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'add_supplier.html', {'form': form})


@permission_required('procurement.delete_supplier',raise_exception=True)
def delete_supplier(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        supplier.delete()
        return redirect('supplier_list')
    return render(request, 'delete_supplier.html', {'supplier': supplier})


# PurchaseOrder Views
@login_required
def purchaseorder_list(request):
    orders = PurchaseOrder.objects.all()
    return render(request, 'purchaseorder_list.html', {'orders': orders})


@permission_required('procurement.add_purchaseorder',raise_exception=True)
def add_purchaseorder(request):
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('purchaseorder_list')
    else:
        form = PurchaseOrderForm()
    return render(request, 'add_purchaseorder.html', {'form': form})


@permission_required('procurement.change_purchaseorder',raise_exception=True)
def update_purchaseorder(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('purchaseorder_list')
    else:
        form = PurchaseOrderForm(instance=order)
    return render(request, 'add_purchaseorder.html', {'form': form})


@permission_required('procurement.delete_purchaseorder',raise_exception=True)
def delete_purchaseorder(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    if request.method == 'POST':
        order.delete()
        return redirect('purchaseorder_list')
    return render(request, 'delete_purchaseorder.html', {'order': order})
