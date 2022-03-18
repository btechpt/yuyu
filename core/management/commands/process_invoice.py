import logging
from typing import Mapping, Dict, Iterable

from django.core.management import BaseCommand
from django.utils import timezone

from core.models import Invoice, InvoiceComponentMixin
from core.component import component, labels
from core.utils.dynamic_setting import get_dynamic_setting, BILLING_ENABLED, INVOICE_TAX

LOG = logging.getLogger("yuyu_new_invoice")


class Command(BaseCommand):
    help = 'Yuyu New Invoice'

    def handle(self, *args, **options):
        print("Processing Invoice")
        if not get_dynamic_setting(BILLING_ENABLED):
            return

        self.close_date = timezone.now()
        self.tax_pertentage = get_dynamic_setting(INVOICE_TAX)

        active_invoices = Invoice.objects.filter(state=Invoice.InvoiceState.IN_PROGRESS).all()
        for active_invoice in active_invoices:
            self.close_active_invoice(active_invoice)
        print("Processing Done")

    def close_active_invoice(self, active_invoice: Invoice):
        active_components_map: Dict[str, Iterable[InvoiceComponentMixin]] = {}

        for label in labels.INVOICE_COMPONENT_LABELS:
            active_components_map[label] = getattr(active_invoice, label).filter(end_date=None).all()

            # Close Invoice Component
            for active_component in active_components_map[label]:
                active_component.close(self.close_date)

        # Finish current invoice
        active_invoice.close(self.close_date, self.tax_pertentage)

        # Creating new Invoice
        new_invoice = Invoice.objects.create(
            project=active_invoice.project,
            start_date=self.close_date,
            state=Invoice.InvoiceState.IN_PROGRESS
        )
        new_invoice.save()

        # Cloning active component to continue in next invoice
        for label, active_components in active_components_map.items():
            handler = component.INVOICE_HANDLER[label]
            for active_component in active_components:
                handler.roll(active_component, self.close_date, update_payload={
                    "invoice": new_invoice
                })
