import logging
from typing import List

from django.core.management import BaseCommand
from django.utils import timezone

from core.models import Invoice, InvoiceInstance, InvoiceFloatingIp, InvoiceVolume

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

        # Close Active Floating
        active_ips: List[InvoiceFloatingIp] = active_invoice.floating_ips.filter(end_date=None).all()
        for ip in active_ips:
            ip.end_date = self.close_date
            ip.save()

        # Close Active Volume
        active_volumes: List[InvoiceVolume] = active_invoice.volumes.filter(end_date=None).all()
        for volume in active_volumes:
            volume.end_date = self.close_date
            volume.save()

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

        # Cloning Active Ips to Continue in next invoice
        # Using the same price
        for ip in active_ips:
            InvoiceFloatingIp.objects.create(
                invoice=new_invoice,
                fip_id=ip.fip_id,
                ip=ip.ip,
                current_state=ip.current_state,
                start_date=ip.end_date,
                daily_price=ip.daily_price,
                monthly_price=ip.monthly_price,
            )

        # Cloning Active Volumes to Continue in next invoice
        # Using the same price
        for volume in active_volumes:
            InvoiceVolume.objects.create(
                invoice=new_invoice,
                volume_id=volume.volume_id,
                volume_name=volume.volume_name,
                volume_type_id=volume.volume_type_id,
                space_allocation_gb=volume.space_allocation_gb,
                current_state=volume.current_state,
                start_date=volume.end_date,
                daily_price=volume.daily_price,
                monthly_price=volume.monthly_price,
            )
