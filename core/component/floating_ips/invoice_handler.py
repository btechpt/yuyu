from core.exception import PriceNotFound
from core.models import FloatingIpsPrice, InvoiceFloatingIp, PriceMixin
from core.component.base.invoice_handler import InvoiceHandler


class FloatingIpInvoiceHandler(InvoiceHandler):
    INVOICE_CLASS = InvoiceFloatingIp
    KEY_FIELD = "fip_id"
    PRICE_DEPENDENCY_FIELDS = []
    INFORMATIVE_FIELDS = ["ip"]

    def get_price(self, payload) -> PriceMixin:
        price = FloatingIpsPrice.objects.first()

        if price is None:
            raise PriceNotFound(identifier='floating ip')

        return price

