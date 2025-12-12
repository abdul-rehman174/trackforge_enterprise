from django.shortcuts import render, redirect, get_object_or_404
from .models import Stock
from .forms import StockForm

def stock_list(request):
    stocks = Stock.objects.all()
    return render(request, 'stock_list.html', {'stocks': stocks})

def add_stock(request):
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('stock_list')
    else:
        form = StockForm()
    return render(request, 'add_stock.html', {'form': form})

def update_stock(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    if request.method == 'POST':
        form = StockForm(request.POST, instance=stock)
        if form.is_valid():
            form.save()
            return redirect('stock_list')
    else:
        form = StockForm(instance=stock)
    return render(request, 'add_stock.html', {'form': form})

def delete_stock(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    if request.method == 'POST':
        stock.delete()
        return redirect('stock_list')
    return render(request, 'delete_stock.html', {'stock': stock})
