from core.exception import PriceNotFound
from core.models import VolumePrice, InvoiceVolume, PriceMixin
from core.component.base.invoice_handler import InvoiceHandler


class VolumeInvoiceHandler(InvoiceHandler):
    INVOICE_CLASS = InvoiceVolume
    KEY_FIELD = "volume_id"
    PRICE_DEPENDENCY_FIELDS = ['volume_type_id', 'space_allocation_gb']
    INFORMATIVE_FIELDS = ['volume_name']

    def get_price(self, payload) -> PriceMixin:
        price = VolumePrice.objects.filter(volume_type_id=payload['volume_type_id']).first()

        if price is None:
            raise PriceNotFound(identifier='volume')

        return price
