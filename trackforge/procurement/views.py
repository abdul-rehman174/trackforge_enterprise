from django.contrib.auth.decorators import login_required,permission_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *

# Supplier Views

@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, 'supplier/supplier_list.html', {'suppliers': suppliers})


@permission_required('procurement.add_supplier',raise_exception=True)
def add_supplier(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('supplier_list')
    else:
        form = SupplierForm()
    return render(request, 'supplier/add_supplier.html', {'form': form})


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
    return render(request, 'supplier/add_supplier.html', {'form': form})


@permission_required('procurement.delete_supplier',raise_exception=True)
def delete_supplier(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        supplier.delete()
        return redirect('supplier_list')
    return render(request, 'supplier/delete_supplier.html', {'supplier': supplier})


from django.shortcuts import render, get_object_or_404
from .models import PurchaseOrder


@login_required
def purchaseorder_list(request):
    # Fixed ordering: Newest POs appear first
    orders = PurchaseOrder.objects.all().order_by('-id')

    # Logic for the professional stat cards
    stats = {
        'total': orders.count(),
        'pending': orders.filter(status__in=['draft', 'submitted']).count(),
        'received': orders.filter(status='completed').count(),
        'cancelled': orders.filter(status='cancelled').count(),
    }

    return render(request, 'purchaseorder/purchaseorder_list.html', {
        'orders': orders,
        'stats': stats
    })


def po_detail(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)

    # 1. Get the items and convert them to a LIST immediately
    # This prevents the template from re-fetching "empty" objects from the DB.
    items = list(order.items.all())

    grand_total = 0
    for item in items:
        # 2. Attach the math to each item in the list
        item.line_total = item.quantity * item.unit_price
        grand_total += item.line_total

    return render(request, 'purchaseorder/po_detail.html', {
        'order': order,
        'items': items,  # Pass the calculated LIST, not the queryset
        'grand_total': grand_total
    })
def add_po(request):
    if request.method == 'POST':
        po_form = PurchaseOrderForm(request.POST)
        # Force the prefix to 'items'
        formset = POLineItemFormSet(request.POST, prefix='items')

        if po_form.is_valid() and formset.is_valid():
            purchase_order = po_form.save()
            # Save items linked to the order
            items = formset.save(commit=False)
            for item in items:
                item.purchase_order = purchase_order
                item.save()
            return redirect('purchaseorder_list')
    else:
        po_form = PurchaseOrderForm()
        # Use the same prefix for the empty forms
        formset = POLineItemFormSet(prefix='items')

    return render(request, "purchaseorder/add_po.html", {
        "po_form": po_form,
        "formset": formset
    })