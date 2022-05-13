from core.component.base.invoice_handler import InvoiceHandler
from core.exception import PriceNotFound
from core.models import PriceMixin, InvoiceSnapshot, SnapshotPrice


class SnapshotInvoiceHandler(InvoiceHandler):
    INVOICE_CLASS = InvoiceSnapshot
    KEY_FIELD = "snapshot_id"
    PRICE_DEPENDENCY_FIELDS = ["space_allocation_gb"]
    INFORMATIVE_FIELDS = ["name"]

    def get_price(self, payload) -> PriceMixin:
        price = SnapshotPrice.objects.first()
        if price is None:
            raise PriceNotFound(identifier='snapshot')

        return price
