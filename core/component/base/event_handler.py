import abc

from django.db import transaction
from django.utils import timezone

from core.models import Invoice, BillingProject
from core.component.base.invoice_handler import InvoiceHandler


class EventHandler(metaclass=abc.ABCMeta):
    def __init__(self, invoice_handler):
        self.invoice_handler: InvoiceHandler = invoice_handler

    def get_tenant_progress_invoice(self, tenant_id):
        """
        Get in progress invoice for specific tenant id.
        Will create new instance if active invoice not found.
        And will create new billing project if tenant id not found.
        :param tenant_id: Tenant id to get the invoice from.
        :return:
        """
        invoice = Invoice.objects.filter(project__tenant_id=tenant_id, state=Invoice.InvoiceState.IN_PROGRESS).first()
        if not invoice:
            project = BillingProject.objects.get_or_create(tenant_id=tenant_id)
            date_today = timezone.now()
            month_first_day = date_today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            invoice = Invoice.objects.create(
                project=project,
                start_date=month_first_day,
                state=Invoice.InvoiceState.IN_PROGRESS
            )

        return invoice

    @abc.abstractmethod
    def handle(self, event_type, raw_payload):
        """
        Handle event from the message queue
        :param event_type: The event type
        :param raw_payload: Payload inside the message
        :return:
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def clean_payload(self, event_type, raw_payload):
        """
        Clean raw payload into payload that can be accepted by invoice handler
        :param event_type: Current event type
        :param raw_payload: Raw payload from messaging queue
        :return:
        """
        raise NotImplementedError()

    @transaction.atomic
    def handle_create(self, invoice: Invoice, event_type, raw_payload):
        """
        Create new invoice component that will be saved to current invoice.

        You need to call this method manually from handle() if you want to use it.

        :param invoice: The invoice that will be saved into
        :param event_type: Current event type
        :param raw_payload: Raw payload from messaging queue.
        :return:
        """
        payload = self.clean_payload(event_type, raw_payload)
        instance = self.invoice_handler.get_active_instance(invoice, payload)
        if not instance:
            payload['invoice'] = invoice
            payload['start_date'] = timezone.now()

            self.invoice_handler.create(payload, fallback_price=True)

            return True

        return False

    @transaction.atomic
    def handle_delete(self, invoice: Invoice, event_type, raw_payload):
        """
        Close invoice component when delete event occurred.

        You need to call this method manually from handle() if you want to use it.

        :param invoice: The invoice that will be saved into
        :param event_type: Current event type
        :param raw_payload: Raw payload from messaging queue.
        :return:
        """
        payload = self.clean_payload(event_type, raw_payload)
        instance = self.invoice_handler.get_active_instance(invoice, payload)
        if instance:
            self.invoice_handler.update_and_close(instance, payload)
            return True

        return False

    @transaction.atomic
    def handle_update(self, invoice: Invoice, event_type, raw_payload):
        """
        Update invoice component when update event occurred.

        You need to call this method manually from handle() if you want to use it.

        :param invoice: The invoice that will be saved into
        :param event_type: Current event type
        :param raw_payload: Raw payload from messaging queue.
        :return:
        """
        payload = self.clean_payload(event_type, raw_payload)
        instance = self.invoice_handler.get_active_instance(invoice, payload)

        if instance:
            if self.invoice_handler.is_price_dependency_changed(instance, payload):
                self.invoice_handler.roll(instance, close_date=timezone.now(), update_payload=payload, fallback_price=True)
                return True

            if self.invoice_handler.is_informative_changed(instance, payload):
                self.invoice_handler.update(instance, update_payload=payload)
                return True

        return False
