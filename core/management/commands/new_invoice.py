import logging
from typing import List

from django.core.management import BaseCommand
from django.utils import timezone

from core.models import Invoice, InvoiceInstance

LOG = logging.getLogger("rintik_new_invoice")


class Command(BaseCommand):
    help = 'Rintik New Invoice'

    def handle(self, *args, **options):
        self.close_date = timezone.now()
        self.tax_pertentage = 0

        active_invoices = Invoice.objects.filter(state=Invoice.InvoiceState.IN_PROGRESS).all()
        for active_invoice in active_invoices:
            self.close_active_invoice(active_invoice)

    def close_active_invoice(self, active_invoice: Invoice):
        # Close Active instances
        active_instances: List[InvoiceInstance] = active_invoice.instances.filter(end_date=None).all()
        for instance in active_instances:
            instance.end_date = self.close_date
            instance.save()


        # Save current instance
        active_invoice.state = Invoice.InvoiceState.FINISHED
        active_invoice.end_date = self.close_date
        active_invoice.tax = self.tax_pertentage * active_invoice.subtotal
        active_invoice.total = active_invoice.tax + active_invoice.subtotal
        active_invoice.save()

        # Creating new Invoice
        new_invoice = Invoice.objects.create(
            project=active_invoice.project,
            start_date=self.close_date,
            state=Invoice.InvoiceState.IN_PROGRESS
        )
        new_invoice.save()

        # Cloning Active Instance to Continue in next invoice
        # Using the same price
        for instance in active_instances:
            InvoiceInstance.objects.create(
                invoice=new_invoice,
                instance_id=instance.instance_id,
                name=instance.name,
                flavor_id=instance.flavor_id,
                current_state=instance.current_state,
                start_date=instance.end_date,
                daily_price=instance.daily_price,
                monthly_price=instance.monthly_price,
            )

