from django.shortcuts import render, redirect, get_object_or_404
from .models import Warehouse
from .forms import WarehouseForm

def warehouse_list(request):
    warehouses = Warehouse.objects.all()
    return render(request, 'warehouse_list.html', {'warehouses': warehouses})

def add_warehouse(request):
    if request.method == 'POST':
        form = WarehouseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('warehouse_list')
    else:
        form = WarehouseForm()
    return render(request, 'add_warehouse.html', {'form': form})

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

def delete_warehouse(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    if request.method == 'POST':
        warehouse.delete()
        return redirect('warehouse_list')
    return render(request, 'delete_warehouse.html', {'warehouse': warehouse})
