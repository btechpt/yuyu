from calendar import monthrange
from datetime import timedelta

from django.db import models
from django.utils import timezone
from djmoney.models.fields import MoneyField


class FlavorPrice(models.Model):
    flavor_id = models.CharField(max_length=256)
    daily_price = MoneyField(max_digits=10, decimal_places=0)
    monthly_price = MoneyField(max_digits=10, decimal_places=0)


class FloatingIpsPrice(models.Model):
    daily_price = MoneyField(max_digits=10, decimal_places=0)
    monthly_price = MoneyField(max_digits=10, decimal_places=0)


class VolumePrice(models.Model):
    volume_type_id = models.CharField(max_length=256)
    daily_price = MoneyField(max_digits=10, decimal_places=0)
    monthly_price = MoneyField(max_digits=10, decimal_places=0)


class BillingProject(models.Model):
    tenant_id = models.CharField(max_length=256)


class Invoice(models.Model):
    class InvoiceState(models.IntegerChoices):
        IN_PROGRESS = 1
        FINISHED = 100

    project = models.ForeignKey('BillingProject', on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(default=None, blank=True, null=True)
    state = models.IntegerField(choices=InvoiceState.choices)
    tax = MoneyField(max_digits=10, decimal_places=0, default=None, blank=True, null=True)
    total = MoneyField(max_digits=10, decimal_places=0, default=None, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    @property
    def subtotal(self):
        # Need to optimize? currently price is calculated on the fly, maybe need to save to db to make performance faster?
        # Instance Price
        instance_price = sum(map(lambda x: x.price_charged, self.instances.all()))

        # TODO: Add other price
        return instance_price


class InvoiceInstance(models.Model):
    invoice = models.ForeignKey('Invoice', on_delete=models.CASCADE, related_name='instances')
    instance_id = models.CharField(max_length=266)
    name = models.CharField(max_length=256)
    flavor_id = models.CharField(max_length=256)
    current_state = models.CharField(max_length=256)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(default=None, blank=True, null=True)
    daily_price = MoneyField(max_digits=10, decimal_places=0)
    monthly_price = MoneyField(max_digits=10, decimal_places=0)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    @property
    def price_charged(self):
        # TODO: Fix price calculation
        # Currently only calculate daily price and it can return zero if end date not yet 1 day

        current_date = timezone.now()
        if self.end_date:
            end_date = self.end_date
        else:
            end_date = current_date

        # TODO: For Testing, please delete
        end_date += timedelta(days=1)

        days = (end_date - self.start_date).days
        return self.daily_price * days


class InvoiceFloatingIp(models.Model):
    invoice = models.ForeignKey('Invoice', on_delete=models.CASCADE, related_name='floating_ips')
    fip_id = models.CharField(max_length=266)
    ip = models.CharField(max_length=256)
    current_state = models.CharField(max_length=256)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    daily_price = MoneyField(max_digits=10, decimal_places=0)
    monthly_price = MoneyField(max_digits=10, decimal_places=0)
    created_at = models.DateTimeField(auto_created=True)
    updated_at = models.DateTimeField(auto_now=True)


class InvoiceVolume(models.Model):
    invoice = models.ForeignKey('Invoice', on_delete=models.CASCADE, related_name='volumes')
    volume_id = models.CharField(max_length=266)
    volume_type_id = models.CharField(max_length=266)
    space_allocation_gb = models.IntegerField()
    current_state = models.CharField(max_length=256)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    daily_price = MoneyField(max_digits=10, decimal_places=0)
    monthly_price = MoneyField(max_digits=10, decimal_places=0)
    created_at = models.DateTimeField(auto_created=True)
    updated_at = models.DateTimeField(auto_now=True)
