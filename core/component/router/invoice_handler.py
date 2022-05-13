from core.component.base.invoice_handler import InvoiceHandler
from core.exception import PriceNotFound
from core.models import PriceMixin, InvoiceRouter, RouterPrice


class RouterInvoiceHandler(InvoiceHandler):
    INVOICE_CLASS = InvoiceRouter
    KEY_FIELD = "router_id"
    PRICE_DEPENDENCY_FIELDS = []
    INFORMATIVE_FIELDS = ["name"]

    def get_price(self, payload) -> PriceMixin:
        price = RouterPrice.objects.first()
        if price is None:
            raise PriceNotFound(identifier='router')

        return price
