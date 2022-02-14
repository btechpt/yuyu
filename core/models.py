import math

from django.conf import settings
from django.db import models
from django.utils import timezone
from djmoney.models.fields import MoneyField
from djmoney.money import Money

from core.component import labels
from core.utils.model_utils import BaseModel, TimestampMixin, PriceMixin, InvoiceComponentMixin


# region Dynamic Setting
class DynamicSetting(BaseModel):
    class DataType(models.IntegerChoices):
        BOOLEAN = 1
        INT = 2
        STR = 3
        JSON = 4

    key = models.CharField(max_length=256, unique=True, db_index=True)
    value = models.TextField()
    type = models.IntegerField(choices=DataType.choices)


# end region

# region Pricing
class FlavorPrice(BaseModel, TimestampMixin, PriceMixin):
    flavor_id = models.CharField(max_length=256)


class FloatingIpsPrice(BaseModel, TimestampMixin, PriceMixin):
    # No need for any additional field
    pass


class VolumePrice(BaseModel, TimestampMixin, PriceMixin):
    volume_type_id = models.CharField(max_length=256)


class RouterPrice(BaseModel, TimestampMixin, PriceMixin):
    # No need for any additional field
    pass


class SnapshotPrice(BaseModel, TimestampMixin, PriceMixin):
    # No need for any additional field
    pass


class ImagePrice(BaseModel, TimestampMixin, PriceMixin):
    # No need for any additional field
    pass


# end region

# region Invoicing
class BillingProject(BaseModel, TimestampMixin):
    tenant_id = models.CharField(max_length=256)


class Invoice(BaseModel, TimestampMixin):
    class InvoiceState(models.IntegerChoices):
        IN_PROGRESS = 1
        UNPAID = 2
        FINISHED = 100

    project = models.ForeignKey('BillingProject', on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(default=None, blank=True, null=True)
    finish_date = models.DateTimeField(default=None, blank=True, null=True)
    state = models.IntegerField(choices=InvoiceState.choices)
    tax = MoneyField(max_digits=10, decimal_places=0, default=None, blank=True, null=True)
    total = MoneyField(max_digits=10, decimal_places=0, default=None, blank=True, null=True)

    @property
    def subtotal(self):
        # Need to optimize?
        # currently price is calculated on the fly, maybe need to save to db to make performance faster?
        # or using cache?

        price = 0
        for component_relation_label in labels.INVOICE_COMPONENT_LABELS:
            relation_all_row = getattr(self, component_relation_label).all()
            price += sum(map(lambda x: x.price_charged, relation_all_row))

        if price == 0:
            return Money(amount=price, currency=settings.DEFAULT_CURRENCY)

        return price

    @property
    def total_resource(self):
        total = 0
        for component_relation_label in labels.INVOICE_COMPONENT_LABELS:
            total += getattr(self, component_relation_label).count()

        return total

    def close(self, date, tax_percentage):
        self.state = Invoice.InvoiceState.UNPAID
        self.end_date = date
        self.tax = tax_percentage * self.subtotal
        self.total = self.tax + self.subtotal
        self.save()

    def finish(self):
        self.state = Invoice.InvoiceState.FINISHED
        self.finish_date = timezone.now()
        self.save()

    def rollback_to_unpaid(self):
        self.state = Invoice.InvoiceState.UNPAID
        self.finish_date = None
        self.save()


# end region

# region Invoice Component
class InvoiceInstance(BaseModel, InvoiceComponentMixin):
    invoice = models.ForeignKey('Invoice', on_delete=models.CASCADE, related_name=labels.LABEL_INSTANCES)
    # Key
    instance_id = models.CharField(max_length=266)

    # Price Dependency
    flavor_id = models.CharField(max_length=256)

    # Informative
    name = models.CharField(max_length=256)


class InvoiceFloatingIp(BaseModel, InvoiceComponentMixin):
    invoice = models.ForeignKey('Invoice', on_delete=models.CASCADE, related_name=labels.LABEL_FLOATING_IPS)
    # Key
    fip_id = models.CharField(max_length=266)

    # Informative
    ip = models.CharField(max_length=256)


class InvoiceVolume(BaseModel, InvoiceComponentMixin):
    invoice = models.ForeignKey('Invoice', on_delete=models.CASCADE, related_name=labels.LABEL_VOLUMES)
    # Key
    volume_id = models.CharField(max_length=256)

    # Price Dependency
    volume_type_id = models.CharField(max_length=256)
    space_allocation_gb = models.FloatField()

    # Informative
    volume_name = models.CharField(max_length=256)

    @property
    def price_charged(self):
        price_without_allocation = super().price_charged
        return price_without_allocation * math.ceil(self.space_allocation_gb)


class InvoiceRouter(BaseModel, InvoiceComponentMixin):
    invoice = models.ForeignKey('Invoice', on_delete=models.CASCADE, related_name=labels.LABEL_ROUTERS)
    # Key
    router_id = models.CharField(max_length=256)

    # Informative
    name = models.CharField(max_length=256)


class InvoiceSnapshot(BaseModel, InvoiceComponentMixin):
    invoice = models.ForeignKey('Invoice', on_delete=models.CASCADE, related_name=labels.LABEL_SNAPSHOTS)
    # Key
    snapshot_id = models.CharField(max_length=256)

    # Price Dependency
    space_allocation_gb = models.FloatField()

    # Informative
    name = models.CharField(max_length=256)

    @property
    def price_charged(self):
        price_without_allocation = super().price_charged
        return price_without_allocation * math.ceil(self.space_allocation_gb)


class InvoiceImage(BaseModel, InvoiceComponentMixin):
    invoice = models.ForeignKey('Invoice', on_delete=models.CASCADE, related_name=labels.LABEL_IMAGES)
    # Key
    image_id = models.CharField(max_length=256)

    # Price Dependency
    space_allocation_gb = models.FloatField()

    # Informative
    name = models.CharField(max_length=256)

    @property
    def price_charged(self):
        price_without_allocation = super().price_charged
        return price_without_allocation * math.ceil(self.space_allocation_gb)
# end region
