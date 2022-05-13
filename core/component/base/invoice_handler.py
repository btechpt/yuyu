import abc

from django.conf import settings
from django.utils import timezone
from djmoney.money import Money

from core.exception import PriceNotFound
from core.models import InvoiceComponentMixin, PriceMixin


class InvoiceHandler(metaclass=abc.ABCMeta):
    INVOICE_CLASS = None
    KEY_FIELD = None
    INFORMATIVE_FIELDS = []
    PRICE_DEPENDENCY_FIELDS = []

    def create(self, payload, fallback_price=False):
        """
        Create new invoice component
        :param payload: the data that will be created
        :param fallback_price: Whether use 0 price if price not found
        :return:
        """
        try:
            price = self.get_price(payload)
            if price is None:
                raise PriceNotFound()
        except PriceNotFound:
            if fallback_price:
                price = PriceMixin()
                price.hourly_price = Money(amount=0, currency=settings.DEFAULT_CURRENCY)
                price.monthly_price = Money(amount=0, currency=settings.DEFAULT_CURRENCY)
            else:
                raise

        payload['hourly_price'] = price.hourly_price
        payload['monthly_price'] = price.monthly_price

        self.INVOICE_CLASS.objects.create(**payload)

    def delete(self):
        self.INVOICE_CLASS.objects.all().delete()

    def roll(self, instance: InvoiceComponentMixin, close_date, update_payload=None, fallback_price=False):
        """
        Roll current instance.
        Close current component instance and clone it
        :param instance: The instance that want to be rolled
        :param close_date: The close date of current instance
        :param update_payload: New data to update the next component instance
        :param fallback_price: Whether use 0 price if price not found
        :return:
        """
        if update_payload is None:
            update_payload = {}

        if not instance.is_closed():
            instance.close(close_date)

        # Set primary ke to None, this will make save() to create a new row
        instance.pk = None

        instance.start_date = instance.end_date
        instance.end_date = None

        instance.created_at = None
        instance.updated_at = None

        # Update the new instance without saving
        instance = self.update(instance, update_payload, save=False)

        # Update the price
        try:
            price = self.get_price(self.get_price_dependency_from_instance(instance))
            if price is None:
                raise PriceNotFound()
        except PriceNotFound:
            if fallback_price:
                price = PriceMixin()
                price.hourly_price = Money(amount=0, currency=settings.DEFAULT_CURRENCY)
                price.monthly_price = Money(amount=0, currency=settings.DEFAULT_CURRENCY)
            else:
                raise
        instance.hourly_price = price.hourly_price
        instance.monthly_price = price.monthly_price
        instance.save()

        return instance

    def update(self, instance, update_payload, save=True):
        """
        Update instance
        :param instance: instance that will be updated
        :param update_payload: new data
        :param save: will it be saved or not
        :return:
        """
        for key, value in update_payload.items():
            setattr(instance, key, value)

        if save:
            instance.save()

        return instance

    def update_and_close(self, instance, payload):
        """
        :param instance: Instance that will be closed
        :param payload: update payload
        :return:
        """
        self.update(instance, payload, save=False)
        instance.close(timezone.now())  # Close will also save the instance

    def is_informative_changed(self, instance, payload):
        """
        Check whether informative field in instance is changed compared to the payload
        :param instance: the instance that will be checked
        :param payload: payload to compare
        :return:
        """
        for informative in self.INFORMATIVE_FIELDS:
            if getattr(instance, informative) != payload[informative]:
                return True

        return False

    def is_price_dependency_changed(self, instance, payload):
        """
        Check whether price dependency field in instance is changed compared to the payload
        :param instance: the instance that will be checked
        :param payload: payload to compare
        :return:
        """
        for price_dependency in self.PRICE_DEPENDENCY_FIELDS:
            if getattr(instance, price_dependency) != payload[price_dependency]:
                return True

        return False

    def get_active_instance(self, invoice, payload):
        """
        Get currently active invoice component instance.
        Filtered by invoice and key field in payload
        :param invoice: Invoice target
        :param payload: Payload to get key field, please make sure there are value for the key field inside the payload
        :return:
        """
        kwargs = {"invoice": invoice, "end_date": None, self.KEY_FIELD: payload[self.KEY_FIELD]}
        return self.INVOICE_CLASS.objects.filter(**kwargs).first()

    def get_price_dependency_from_instance(self, instance):
        """
        Get payload with price dependency field extracted from instance
        :param instance: Instance to extract the price dependency
        :return:
        """
        return {field: getattr(instance, field) for field in self.PRICE_DEPENDENCY_FIELDS}

    @abc.abstractmethod
    def get_price(self, payload) -> PriceMixin:
        """
        Get price based on payload
        :param payload: the payload that will contain filter to get the price
        :return:
        """
        raise NotImplementedError()
