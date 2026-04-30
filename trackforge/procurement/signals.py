from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum
from .models import PurchaseOrder
from inventory.models import Stock, StockTransaction


@receiver(post_save, sender=PurchaseOrder)
def update_purchase_order_on_status_choices(sender, instance, **kwargs):
    """Reconcile stock against PO status changes.

    Runs on_commit so that POLineItems saved alongside the PO are visible.
    Each branch is idempotent — re-saving the PO at the same status is a no-op.
    """

    def run_stock_update():
        # Skip if still in planning stages
        if instance.status in ("draft", "submitted"):
            return

        ref = f"PO: {instance.reference_number}"

        # Defense-in-depth: a cancelled PO is a closed book. Even if some path
        # bypasses the model-level lock and flips it back to completed/partial,
        # we refuse to move stock again.
        cancel_logged = StockTransaction.objects.filter(
            reference_document=ref,
            transaction_type="po_cancel",
        ).exists()
        if cancel_logged and instance.status != "cancelled":
            return

        with transaction.atomic():
            # STATUS: COMPLETED — top up to ordered qty, once
            if instance.status == "completed":
                already_completed = StockTransaction.objects.filter(
                    reference_document=ref,
                    transaction_type="po_complete",
                ).exists()
                if already_completed:
                    return

                for item in instance.items.all():
                    partial_history = StockTransaction.objects.filter(
                        reference_document=ref,
                        stock__product=item.product,
                        transaction_type="po_partial",
                    ).aggregate(total=Sum("quantity_changed"))["total"] or 0

                    remaining_to_add = item.quantity - partial_history
                    if remaining_to_add <= 0:
                        continue

                    stock, _ = Stock.objects.select_for_update().get_or_create(
                        product=item.product,
                        warehouse=instance.warehouse,
                        defaults={"quantity": 0},
                    )
                    stock.quantity += remaining_to_add
                    stock.save()

                    StockTransaction.objects.create(
                        stock=stock,
                        transaction_type="po_complete",
                        quantity_changed=remaining_to_add,
                        stock_after_transaction=stock.quantity,
                        reference_document=ref,
                    )

            # STATUS: PARTIAL — wave-based delivery, top up the gap
            elif instance.status == "partial":
                for item in instance.items.all():
                    history = StockTransaction.objects.filter(
                        reference_document=ref,
                        stock__product=item.product,
                        transaction_type="po_partial",
                    ).aggregate(total=Sum("quantity_changed"))["total"] or 0

                    amount_to_add = item.quantity_received - history
                    if amount_to_add <= 0:
                        continue

                    stock, _ = Stock.objects.select_for_update().get_or_create(
                        product=item.product,
                        warehouse=instance.warehouse,
                        defaults={"quantity": 0},
                    )
                    stock.quantity += amount_to_add
                    stock.save()

                    StockTransaction.objects.create(
                        stock=stock,
                        transaction_type="po_partial",
                        quantity_changed=amount_to_add,
                        stock_after_transaction=stock.quantity,
                        reference_document=ref,
                    )

            # STATUS: CANCELLED — undo all additions, once
            elif instance.status == "cancelled":
                already_cancelled = StockTransaction.objects.filter(
                    reference_document=ref,
                    transaction_type="po_cancel",
                ).exists()
                if already_cancelled:
                    return

                for item in instance.items.all():
                    history_to_undo = StockTransaction.objects.filter(
                        reference_document=ref,
                        stock__product=item.product,
                        transaction_type__in=["po_complete", "po_partial"],
                    ).aggregate(total=Sum("quantity_changed"))["total"] or 0

                    if history_to_undo <= 0:
                        continue

                    stock = (
                        Stock.objects.select_for_update()
                        .filter(product=item.product, warehouse=instance.warehouse)
                        .first()
                    )
                    if stock is None:
                        continue

                    stock.quantity -= history_to_undo
                    stock.save()

                    StockTransaction.objects.create(
                        stock=stock,
                        transaction_type="po_cancel",
                        quantity_changed=-history_to_undo,
                        stock_after_transaction=stock.quantity,
                        reference_document=ref,
                    )

    transaction.on_commit(run_stock_update)
