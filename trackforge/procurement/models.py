from django.core.exceptions import ValidationError
from django.db import models
from core.models import AuditableModel
from inventory.models import Product, Warehouse


# Statuses that lock a PO from any further status changes. Once a PO is
# completed or cancelled, the books are closed — flipping status again would
# corrupt the stock audit trail.
LOCKED_STATUSES = ("completed", "cancelled")


class Supplier(AuditableModel):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name


class PurchaseOrder(AuditableModel):

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('partial', 'Partially Received'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='purchase_orders')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name='purchase_orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    order_date = models.DateField(auto_now_add=True)

    # We will use this later for our automation logic
    reference_number = models.CharField(max_length=50, unique=True, help_text="Internal PO Number")

    def __str__(self):
        return f"{self.reference_number} - {self.supplier.name}"

    def clean(self):
        super().clean()
        if not self.pk:
            return
        old_status = (
            PurchaseOrder.objects.filter(pk=self.pk)
            .values_list("status", flat=True)
            .first()
        )
        if old_status in LOCKED_STATUSES and old_status != self.status:
            raise ValidationError({
                "status": (
                    f"This order is {old_status.title()} and cannot be changed. "
                    "Locked orders preserve the stock audit trail."
                )
            })

    def save(self, *args, **kwargs):
        # Defense-in-depth: enforce the lock even on direct .save() calls
        # (admin, shell, signals) — not just ModelForm-driven paths.
        self.clean()
        super().save(*args, **kwargs)


class POLineItem(models.Model):
    """The individual items inside a Purchase Order"""
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price at time of purchase")
    quantity_received = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="The amount that has actually arrived in the warehouse",
    )

    def __str__(self):
        return f"{self.quantity} x {self.product.name} ({self.purchase_order.reference_number})"