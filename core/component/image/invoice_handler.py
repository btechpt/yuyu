from core.component.base.invoice_handler import InvoiceHandler
from core.models import PriceMixin, InvoiceImage, ImagePrice


class ImageInvoiceHandler(InvoiceHandler):
    INVOICE_CLASS = InvoiceImage
    KEY_FIELD = "image_id"
    PRICE_DEPENDENCY_FIELDS = ["space_allocation_gb"]
    INFORMATIVE_FIELDS = ["name"]

    def get_price(self, payload) -> PriceMixin:
        return ImagePrice.objects.first()
