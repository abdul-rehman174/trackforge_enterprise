from django.db import models

# Create your models here.
class Supplier(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    def __str__(self):
        return self.name


class PurchaseOrder(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[('draft', 'Draft'), ('ordered', 'Ordered'), ('received', 'Received')],
        default='draft'
    )

    def __str__(self):
        return f"PO-{self.id} ({self.supplier.name})"
