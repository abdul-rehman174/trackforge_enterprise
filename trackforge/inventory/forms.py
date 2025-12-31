from django import forms
from .models import Category, Warehouse,Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name","sku","category","description","cost_price","selling_price"]


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name'] # Slug is handled in the view


class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['name', 'code', 'location', 'is_active']