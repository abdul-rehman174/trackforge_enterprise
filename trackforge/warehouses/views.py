from django.contrib.auth.decorators import login_required,permission_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Warehouse
from .forms import WarehouseForm

@login_required
def warehouse_list(request):
    warehouses = Warehouse.objects.all()
    return render(request, 'warehouse_list.html', {'warehouses': warehouses})


@permission_required('warehouses.add_warehouse',raise_exception=True)
def add_warehouse(request):
    if request.method == 'POST':
        form = WarehouseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('warehouse_list')
    else:
        form = WarehouseForm()
    return render(request, 'add_warehouse.html', {'form': form})


@permission_required('warehouses.change_warehouse',raise_exception=True)
def update_warehouse(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    if request.method == 'POST':
        form = WarehouseForm(request.POST, instance=warehouse)
        if form.is_valid():
            form.save()
            return redirect('warehouse_list')
    else:
        form = WarehouseForm(instance=warehouse)
    return render(request, 'add_warehouse.html', {'form': form})


@permission_required('warehouses.delete_warehouse',raise_exception=True)
def delete_warehouse(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    if request.method == 'POST':
        warehouse.delete()
        return redirect('warehouse_list')
    return render(request, 'delete_warehouse.html', {'warehouse': warehouse})
