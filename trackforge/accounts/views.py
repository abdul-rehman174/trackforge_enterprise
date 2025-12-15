from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render,redirect,HttpResponse
from .models import CustomUser
from .forms import CustomUserForm
from inventory.models import Product
from warehouses.models import Warehouse
from stock.models import Stock
from procurement.models import Supplier, PurchaseOrder
from django.contrib import auth
# Create your views here.


def dashboard(request):
    """Home page linking to all sections with summary counts"""
    context = {
        'user_count': CustomUser.objects.count(),
        'product_count': Product.objects.count(),
        'warehouse_count': Warehouse.objects.count(),
        'stock_count': Stock.objects.count(),
        'supplier_count': Supplier.objects.count(),
        'po_count': PurchaseOrder.objects.count(),
    }
    return render(request, 'dashboard.html', context)


def register_user(request):
    if request.method == "POST":
        form = CustomUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            return redirect("login")
    else:
        form = CustomUserForm()
    return render(request,"register_user.html",{"form":form ,"button_label":"Register"})


def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = auth.authenticate(request,username=username,password=password)
        if user:
            auth.login(request,user)
            return redirect('/')

    return render(request,"login.html")

def logout(request):
    auth.logout(request)
    return redirect('/')

@login_required
def user_list(request):
    users = CustomUser.objects.all()
    return render(request,"user_list.html",{"users":users})


@permission_required('accounts.change_customuser',raise_exception=True)
def update_user(request,pk):
    user = CustomUser.objects.get(pk=pk)
    if request.method == "POST":
        form = CustomUserForm(request.POST,instance = user)
        if form.is_valid():
            form.save()
            return redirect("user_list")
    else:
        form = CustomUserForm(instance = user)
        return render(request,"register_user.html",{"form":form, "button_label":"Update"})


@permission_required('accounts.delete_customuser',raise_exception=True)
def delete_user(request, pk):
    user = CustomUser.objects.get(pk=pk)

    if request.method == "POST":
        user.delete()
        return redirect("user_list")
    else:
        return render(request,"delete_user.html",{"user":user})


