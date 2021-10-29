from core.models import FlavorPrice, InvoiceInstance, PriceMixin
from core.component.base.invoice_handler import InvoiceHandler


class InstanceInvoiceHandler(InvoiceHandler):
    INVOICE_CLASS = InvoiceInstance
    KEY_FIELD = "instance_id"
    PRICE_DEPENDENCY_FIELDS = ['flavor_id']
    INFORMATIVE_FIELDS = ['name']

    def get_price(self, payload) -> PriceMixin:
        return FlavorPrice.objects.filter(flavor_id=payload['flavor_id']).first()
