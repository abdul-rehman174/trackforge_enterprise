from django.contrib.auth.decorators import login_required,permission_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Stock
from .forms import StockForm

@login_required
def stock_list(request):
    stocks = Stock.objects.all()
    return render(request, 'stock/stock_list.html', {'stocks': stocks})


@permission_required('stock.add_stock',raise_exception=True)
def add_stock(request):
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('stock_list')
    else:
        form = StockForm()
    return render(request, 'stock/add_stock.html', {'form': form})


@permission_required('stock.change_stock',raise_exception=True)
def update_stock(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    if request.method == 'POST':
        form = StockForm(request.POST, instance=stock)
        if form.is_valid():
            form.save()
            return redirect('stock_list')
    else:
        form = StockForm(instance=stock)
    return render(request, 'stock/add_stock.html', {'form': form})


@permission_required('stock.delete_stock',raise_exception=True)
def delete_stock(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    if request.method == 'POST':
        stock.delete()
        return redirect('stock_list')
    return render(request, 'stock/delete_stock.html', {'stock': stock})
