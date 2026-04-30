from datetime import datetime
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    POLineItemCreateFormSet,
    POLineItemFormSet,
    PurchaseOrderCreateForm,
    PurchaseOrderForm,
    SupplierForm,
)
from .models import POLineItem, PurchaseOrder, Supplier


# Allowed PO status transitions. Once a PO is completed or cancelled
# it is locked — moving back would corrupt the audit trail.
ALLOWED_TRANSITIONS = {
    "draft": ["submitted", "cancelled"],
    "submitted": ["partial", "completed", "cancelled"],
    "partial": ["partial", "completed", "cancelled"],
    "completed": [],
    "cancelled": [],
}


def _next_reference_number():
    """Auto-generate a PO reference like PO-2026-0007."""
    year = datetime.now().year
    prefix = f"PO-{year}-"
    last = (
        PurchaseOrder.objects.filter(reference_number__startswith=prefix)
        .order_by("-reference_number")
        .values_list("reference_number", flat=True)
        .first()
    )
    next_num = 1
    if last:
        try:
            next_num = int(last.rsplit("-", 1)[1]) + 1
        except (ValueError, IndexError):
            next_num = 1
    return f"{prefix}{next_num:04d}"


# --- Supplier views ---

@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, "supplier/supplier_list.html", {"suppliers": suppliers})


@login_required
@permission_required("procurement.add_supplier", raise_exception=True)
def add_supplier(request):
    if request.method == "POST":
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("supplier_list")
    else:
        form = SupplierForm()
    return render(request, "supplier/add_supplier.html", {"form": form})


@login_required
@permission_required("procurement.change_supplier", raise_exception=True)
def update_supplier(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == "POST":
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            return redirect("supplier_list")
    else:
        form = SupplierForm(instance=supplier)
    return render(request, "supplier/add_supplier.html", {"form": form})


@login_required
@permission_required("procurement.delete_supplier", raise_exception=True)
def delete_supplier(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == "POST":
        supplier.delete()
        return redirect("supplier_list")
    return render(request, "supplier/delete_supplier.html", {"supplier": supplier})


# --- Purchase Order views ---

@login_required
def purchaseorder_list(request):
    status_filter = request.GET.get("status", "").strip()
    qs = PurchaseOrder.objects.select_related("supplier", "warehouse").prefetch_related("items").order_by("-id")

    if status_filter and status_filter in dict(PurchaseOrder.STATUS_CHOICES):
        qs = qs.filter(status=status_filter)

    orders = list(qs)
    for o in orders:
        items = list(o.items.all())
        o.items_count = len(items)
        o.grand_total = sum((i.quantity * i.unit_price for i in items), Decimal("0"))

    base = PurchaseOrder.objects.all()
    stats = {
        "total": base.count(),
        "pending": base.filter(status__in=["draft", "submitted", "partial"]).count(),
        "received": base.filter(status="completed").count(),
        "cancelled": base.filter(status="cancelled").count(),
    }

    return render(request, "purchaseorder/purchaseorder_list.html", {
        "orders": orders,
        "stats": stats,
        "status_filter": status_filter,
        "status_choices": PurchaseOrder.STATUS_CHOICES,
    })


@login_required
def po_detail(request, pk):
    order = get_object_or_404(
        PurchaseOrder.objects.select_related("supplier", "warehouse"),
        pk=pk,
    )

    items = list(order.items.select_related("product").all())
    grand_total = Decimal("0")
    for item in items:
        item.line_total = item.quantity * item.unit_price
        grand_total += item.line_total

    return render(request, "purchaseorder/po_detail.html", {
        "order": order,
        "items": items,
        "grand_total": grand_total,
        "allowed_transitions": ALLOWED_TRANSITIONS.get(order.status, []),
    })


@login_required
@permission_required("procurement.add_purchaseorder", raise_exception=True)
def add_po(request):
    if request.method == "POST":
        po_form = PurchaseOrderCreateForm(request.POST)
        formset = POLineItemCreateFormSet(request.POST, prefix="items")

        if po_form.is_valid() and formset.is_valid():
            with transaction.atomic():
                purchase_order = po_form.save(commit=False)
                if not purchase_order.reference_number:
                    purchase_order.reference_number = _next_reference_number()
                purchase_order.status = "draft"
                purchase_order.save()
                formset.instance = purchase_order
                formset.save()
            messages.success(request, f"Purchase Order {purchase_order.reference_number} created as Draft.")
            return redirect("po_detail", pk=purchase_order.pk)
    else:
        po_form = PurchaseOrderCreateForm(initial={"reference_number": _next_reference_number()})
        formset = POLineItemCreateFormSet(prefix="items")

    return render(request, "purchaseorder/add_po.html", {
        "po_form": po_form,
        "formset": formset,
        "is_create": True,
    })


@login_required
@permission_required("procurement.change_purchaseorder", raise_exception=True)
def update_po(request, pk):
    purchase_order = get_object_or_404(PurchaseOrder, pk=pk)

    if purchase_order.status not in ("draft", "submitted"):
        messages.error(request, "Only Draft or Submitted POs can be edited. Use Receive or Cancel for others.")
        return redirect("po_detail", pk=purchase_order.pk)

    if request.method == "POST":
        po_form = PurchaseOrderForm(request.POST, instance=purchase_order)
        formset = POLineItemFormSet(request.POST, instance=purchase_order, prefix="items")

        if po_form.is_valid() and formset.is_valid():
            with transaction.atomic():
                po_form.save()
                formset.save()
            messages.success(request, "Purchase Order updated.")
            return redirect("po_detail", pk=purchase_order.pk)
    else:
        po_form = PurchaseOrderForm(instance=purchase_order)
        formset = POLineItemFormSet(instance=purchase_order, prefix="items")

    return render(request, "purchaseorder/add_po.html", {
        "po_form": po_form,
        "formset": formset,
        "is_create": False,
    })


@login_required
@permission_required("procurement.change_purchaseorder", raise_exception=True)
def receive_po(request, pk):
    """Dedicated receiving view — shows ordered vs already-received vs receiving-now per item."""
    order = get_object_or_404(
        PurchaseOrder.objects.select_related("supplier", "warehouse"),
        pk=pk,
    )

    if order.status in ("completed", "cancelled"):
        messages.error(request, f"PO is {order.get_status_display()} — receiving is closed.")
        return redirect("po_detail", pk=order.pk)

    items = list(order.items.select_related("product").all())

    if request.method == "POST":
        with transaction.atomic():
            all_received = True
            for item in items:
                key = f"receive_{item.pk}"
                raw = request.POST.get(key, "0").strip()
                try:
                    receive_now = Decimal(raw or "0")
                except Exception:
                    messages.error(request, f"Invalid quantity for {item.product.name}.")
                    return redirect("receive_po", pk=order.pk)

                if receive_now < 0:
                    messages.error(request, "Quantities cannot be negative.")
                    return redirect("receive_po", pk=order.pk)

                new_total = item.quantity_received + receive_now
                if new_total > item.quantity:
                    messages.error(
                        request,
                        f"{item.product.name}: cannot receive more than ordered ({item.quantity}).",
                    )
                    return redirect("receive_po", pk=order.pk)

                item.quantity_received = new_total
                item.save(update_fields=["quantity_received"])

                if item.quantity_received < item.quantity:
                    all_received = False

            order.status = "completed" if all_received else "partial"
            order.save()

        messages.success(request, "Receipt recorded — stock updated.")
        return redirect("po_detail", pk=order.pk)

    for item in items:
        item.outstanding = item.quantity - item.quantity_received

    return render(request, "purchaseorder/receive_po.html", {
        "order": order,
        "items": items,
    })


@login_required
@permission_required("procurement.change_purchaseorder", raise_exception=True)
def update_po_status(request, pk):
    if request.method != "POST":
        return redirect("po_detail", pk=pk)

    order = get_object_or_404(PurchaseOrder, pk=pk)
    new_status = request.POST.get("status")

    if not new_status:
        messages.error(request, "No status supplied.")
        return redirect("po_detail", pk=pk)

    if new_status == order.status:
        return redirect("po_detail", pk=pk)

    allowed = ALLOWED_TRANSITIONS.get(order.status, [])
    if new_status not in allowed:
        messages.error(
            request,
            f"Cannot move PO from '{order.get_status_display()}' to '{new_status}'.",
        )
        return redirect("po_detail", pk=pk)

    order.status = new_status
    order.save()
    messages.success(request, f"PO status updated to '{order.get_status_display()}'.")
    return redirect("po_detail", pk=pk)
