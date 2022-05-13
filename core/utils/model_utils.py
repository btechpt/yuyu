import math

from django.db import models
from django.utils import timezone
from djmoney.models.fields import MoneyField


class BaseModel(models.Model):
    class Meta:
        abstract = True


class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class PriceMixin(models.Model):
    hourly_price = MoneyField(max_digits=10, decimal_places=0)
    monthly_price = MoneyField(max_digits=10, decimal_places=0, default=None, blank=True, null=True)

    class Meta:
        abstract = True


class InvoiceComponentMixin(TimestampMixin, PriceMixin):
    """
    Storing start time for price calculation
    """
    start_date = models.DateTimeField()

    """
    Storing end time of the component, when component still active it will be None.
    It will be set when component is closed or rolled
    """
    end_date = models.DateTimeField(default=None, blank=True, null=True)

    @property
    def adjusted_end_date(self):
        """
        Get end date that will be used for calculation. Please use this for calculation and displaying usage duration
        Basically it just return current time if end_date is None
        end_date will be set when invoice is finished every end of the month or when invoice component is rolled
        """
        current_date = timezone.now()
        if self.end_date:
            end_date = self.end_date
        else:
            end_date = current_date

        return end_date

    @property
    def price_charged(self):
        """
        Calculate the price to be charged to user
        """
        end_date = self.adjusted_end_date
        if self.start_date.date().day == 1 and end_date.date().day == 1 \
                and self.start_date.date().month != end_date.date().month \
                and self.monthly_price:
            # Using monthly price
            return self.monthly_price

        seconds_passes = (end_date - self.start_date).total_seconds()
        hour_passes = math.ceil(seconds_passes / 3600)

        return self.hourly_price * hour_passes

    def is_closed(self):
        """
        Is component closed
        """
        return self.end_date is not None

    def close(self, date):
        """
        Close component the component
        """
        self.end_date = date
        self.save()

    class Meta:
        abstract = True

