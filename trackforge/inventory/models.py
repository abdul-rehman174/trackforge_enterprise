from django.db import models
from django.core.exceptions import ValidationError
from core.models import AuditableModel


class Warehouse(AuditableModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True, help_text="Unique code e.g. WH-NY-01")
    location = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Category(AuditableModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Product(AuditableModel):
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=50, unique=True, help_text="Stock Keeping Unit (Unique ID)")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)

    # Financials (Crucial for Reports)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Alerts
    reorder_level = models.PositiveIntegerField(default=10, help_text="Alert when stock falls below this")

    def __str__(self):
        return f"{self.name} ({self.sku})"


class Stock(AuditableModel):
    """
    The 'Live' view of inventory.
    Use this to check 'Do we have enough?'
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_levels')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='stock_levels')
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        unique_together = ('product', 'warehouse')  # Ensures you can't have duplicate rows for same item/loc
        verbose_name_plural = "Stock Levels"

    def __str__(self):
        return f"{self.product.sku} @ {self.warehouse.code}: {self.quantity}"


class StockTransaction(AuditableModel):
    """
    The 'History' view.
    Every time stock changes, a record MUST be created here.
    """
    TX_TYPES =[
        ('po_complete', 'PO Complete'),
        ('po_partial', 'PO Partial'),
        ('po_cancel', 'PO Cancelled'),
    ]

    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=100, choices=TX_TYPES)

    quantity_changed = models.DecimalField(max_digits=12, decimal_places=2,
                                           help_text="Negative for removal, Positive for addition")

    stock_after_transaction = models.DecimalField(max_digits=12, decimal_places=2,
                                                  help_text="Snapshot of balance after this movement")

    reference_document = models.CharField(max_length=100, blank=True, help_text="PO #123 or Order #456")
    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.transaction_type}: {self.quantity_changed} for {self.stock.product.sku}"