from django.shortcuts import render,redirect
from .models import Product
from .forms import *

# Create your views here.
def product_list(request):
    products = Product.objects.all()
    return render(request,"product_list.html",{"products":products})

def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("product_list")
    else:
        form = ProductForm()
        return render(request,"add_product.html",{"form":form})

def update_product(request,pk):
    product = Product.objects.get(pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST,instance = product)
        if form.is_valid():
            form.save()
            return redirect("product_list")
    else:
        form = ProductForm(instance = product)
        return render(request,"add_product.html",{"form":form})


def delete_product(request, pk):
    product = Product.objects.get(pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'delete_product.html', {'product': product})
