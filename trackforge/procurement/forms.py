from django import forms
from django.forms import inlineformset_factory
from .models import POLineItem, PurchaseOrder, Supplier


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ["name", "email", "phone", "address"]


class _LineItemFormMixin:
    """Shared behavior: empty rows (no product picked) are treated as unchanged
    so the formset skips them instead of failing validation."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Clear the model-level default=1 when rendering a fresh row so an
        # untouched empty row really does look untouched to the formset.
        if not self.instance.pk:
            self.fields["quantity"].initial = None
        # Hide the model's pre-existing helptext to keep rows compact.
        for f in self.fields.values():
            f.help_text = ""

    def has_changed(self):
        product_key = self.add_prefix("product")
        product_val = (self.data.get(product_key) or "").strip() if self.data else ""
        if not product_val and not self.instance.pk:
            return False
        return super().has_changed()


# --- Create flow: minimal fields, status auto-set to draft ---

class PurchaseOrderCreateForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ["reference_number", "supplier", "warehouse"]
        widgets = {
            "reference_number": forms.TextInput(attrs={
                "placeholder": "Leave blank to auto-generate",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["reference_number"].required = False


class POLineItemCreateForm(_LineItemFormMixin, forms.ModelForm):
    class Meta:
        model = POLineItem
        fields = ["product", "quantity", "unit_price"]


POLineItemCreateFormSet = inlineformset_factory(
    PurchaseOrder,
    POLineItem,
    form=POLineItemCreateForm,
    extra=1,
    can_delete=True,
)


# --- Edit flow: status is intentionally NOT here. Status changes go through
# the controlled dropdown on the detail page (ALLOWED_TRANSITIONS). ---

class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ["reference_number", "supplier", "warehouse"]


class POLineItemForm(_LineItemFormMixin, forms.ModelForm):
    class Meta:
        model = POLineItem
        fields = ["product", "quantity", "unit_price", "quantity_received"]


POLineItemFormSet = inlineformset_factory(
    PurchaseOrder,
    POLineItem,
    form=POLineItemForm,
    extra=1,
    can_delete=True,
)
