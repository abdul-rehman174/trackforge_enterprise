from django.db import models
from core.models import AuditableModel
from inventory.models import Product, Warehouse


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


class POLineItem(models.Model):
    """The individual items inside a Purchase Order"""
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price at time of purchase")
    quantity_received = models.PositiveIntegerField(
        default=0,
        help_text="The amount that has actually arrived in the warehouse"
    )
    def __str__(self):
        return f"{self.quantity} x {self.product.name} ({self.purchase_order.reference_number})"