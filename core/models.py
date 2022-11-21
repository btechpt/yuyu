import logging
import math
import re

from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.html import strip_tags
from djmoney.models.fields import MoneyField
from djmoney.money import Money

from core.component import labels
from core.component.labels import LABEL_INSTANCES, LABEL_IMAGES, LABEL_SNAPSHOTS, LABEL_ROUTERS, LABEL_FLOATING_IPS, \
    LABEL_VOLUMES
from core.utils.model_utils import BaseModel, TimestampMixin, PriceMixin, InvoiceComponentMixin

LOG = logging.getLogger("yuyu")


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
    flavor_id = models.CharField(max_length=256, unique=True, blank=False)


class FloatingIpsPrice(BaseModel, TimestampMixin, PriceMixin):
    # No need for any additional field
    pass


class VolumePrice(BaseModel, TimestampMixin, PriceMixin):
    volume_type_id = models.CharField(max_length=256, unique=True, blank=False)


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
    email_notification = models.CharField(max_length=512, blank=True, null=True)

    def __str__(self):
        return self.tenant_id


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
    tax = MoneyField(max_digits=10, default=None, blank=True, null=True)
    total = MoneyField(max_digits=10, default=None, blank=True, null=True)

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

    @property
    def state_str(self):
        if self.state == Invoice.InvoiceState.IN_PROGRESS:
            return 'In Progress'

        if self.state == Invoice.InvoiceState.UNPAID:
            return 'Unpaid'

        if self.state == Invoice.InvoiceState.FINISHED:
            return 'Finished'

    def close(self, date, tax_percentage):
        self.state = Invoice.InvoiceState.UNPAID
        self.end_date = date
        self.tax = tax_percentage * self.subtotal / 100
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

    # Price for individual key
    @property
    def instance_price(self):
        relation_all_row = getattr(self, LABEL_INSTANCES).all()
        return sum(map(lambda x: x.price_charged, relation_all_row))

    @property
    def volume_price(self):
        relation_all_row = getattr(self, LABEL_VOLUMES).all()
        return sum(map(lambda x: x.price_charged, relation_all_row))

    @property
    def fip_price(self):
        relation_all_row = getattr(self, LABEL_FLOATING_IPS).all()
        return sum(map(lambda x: x.price_charged, relation_all_row))

    @property
    def router_price(self):
        relation_all_row = getattr(self, LABEL_ROUTERS).all()
        return sum(map(lambda x: x.price_charged, relation_all_row))

    @property
    def snapshot_price(self):
        relation_all_row = getattr(self, LABEL_SNAPSHOTS).all()
        return sum(map(lambda x: x.price_charged, relation_all_row))

    @property
    def images_price(self):
        relation_all_row = getattr(self, LABEL_IMAGES).all()
        return sum(map(lambda x: x.price_charged, relation_all_row))


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

class Notification(BaseModel, TimestampMixin):
    project = models.ForeignKey('BillingProject', on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=256)
    short_description = models.CharField(max_length=524)
    content = models.TextField()
    sent_status = models.BooleanField()
    is_read = models.BooleanField()

    def recipient(self):
        if self.project and self.project.email_notification:
            return self.project.email_notification
        return 'Admin'

    def send(self):
        from core.utils.dynamic_setting import get_dynamic_setting, EMAIL_ADMIN
        try:
            def textify(html):
                # Remove html tags and continuous whitespaces
                text_only = re.sub('[ \t]+', ' ', strip_tags(html))
                # Strip single spaces in the beginning of each line
                return text_only.replace('\n ', '\n').strip()

            recipient = get_dynamic_setting(EMAIL_ADMIN).split(",")
            if self.project and self.project.email_notification:
                recipient += self.project.email_notification.split(",")

            send_mail(
                subject=self.title,
                message=textify(self.content),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient,
                html_message=self.content,
            )
            self.sent_status = True
            self.save()
        except Exception as e:
            LOG.exception('Error sending notification')
            self.sent_status = False
            self.save()
