from core.component.base.invoice_handler import InvoiceHandler
from core.models import PriceMixin, InvoiceSnapshot, SnapshotPrice


class SnapshotInvoiceHandler(InvoiceHandler):
    INVOICE_CLASS = InvoiceSnapshot
    KEY_FIELD = "snapshot_id"
    PRICE_DEPENDENCY_FIELDS = ["space_allocation_gb"]
    INFORMATIVE_FIELDS = ["name"]

    def get_price(self, payload) -> PriceMixin:
        return SnapshotPrice.objects.first()
