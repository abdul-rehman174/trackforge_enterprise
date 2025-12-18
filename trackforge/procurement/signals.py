from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PurchaseOrder
# Note: Using 'Stock' instead of 'StockLevel' to match your model name
from inventory.models import Stock, StockTransaction

@receiver(post_save, sender=PurchaseOrder)
def update_inventory_on_complete(sender, instance, **kwargs):
    # 1. Trigger only on 'completed' status
    if instance.status == 'completed':

        # 2. Check for existing transaction to prevent duplicates
        already_processed = StockTransaction.objects.filter(
            reference_document=f"PO: {instance.reference_number}",
            transaction_type='PO_RCV'
        ).exists()

        if not already_processed:
            for item in instance.items.all():
                # Matches your 'Stock' model name
                stock, _ = Stock.objects.get_or_create(
                    product=item.product,
                    warehouse=instance.warehouse,
                    defaults={'quantity': 0}
                )

                # Use += for your DecimalField quantity
                stock.quantity += item.quantity
                stock.save()

                # Create the Transaction history
                StockTransaction.objects.create(
                    stock=stock,
                    transaction_type='PO_RCV',
                    quantity_changed=item.quantity,
                    stock_after_transaction=stock.quantity,
                    reference_document=f"PO: {instance.reference_number}",
                    created_by=instance.updated_by
                )