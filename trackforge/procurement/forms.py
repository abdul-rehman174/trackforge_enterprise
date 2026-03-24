from django import forms
from .models import *
from django.forms import inlineformset_factory

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ["name",'email',"phone",'address']

class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ["reference_number","supplier","warehouse","status"]

class POLineItemForm(forms.ModelForm):
    class Meta:
        model = POLineItem
        fields = ["product","quantity","unit_price","quantity_received"]

# In your forms.py
POLineItemFormSet = inlineformset_factory(
    PurchaseOrder,
    POLineItem,
    form=POLineItemForm,
    extra=3,
    can_delete=True,
)