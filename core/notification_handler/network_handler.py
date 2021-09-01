from django.db import transaction
from django.utils import timezone

from core.models import Invoice, InvoiceFloatingIp, FloatingIpsPrice


class NetworkHandler:
    def get_tenant_progress_invoice(self, tenant_id):
        return Invoice.objects.filter(project__tenant_id=tenant_id, state=Invoice.InvoiceState.IN_PROGRESS).first()

    def handle(self, event_type, payload):
        if event_type == 'floatingip.create.end':
            tenant_id = payload['floatingip']['tenant_id']

            # Get instance invoice
            invoice = self.get_tenant_progress_invoice(tenant_id)
            if not invoice:
                return

            self.handle_create(invoice, payload)

        if event_type == 'floatingip.delete.end':
            tenant_id = payload['floatingip']['tenant_id']

            # Get instance invoice
            invoice = self.get_tenant_progress_invoice(tenant_id)
            if not invoice:
                return

            self.handle_delete(invoice, payload)

    @transaction.atomic
    def handle_create(self, invoice: Invoice, payload):
        fip_id = payload['floatingip']['id']
        ip = payload['floatingip']['floating_ip_address']
        is_exists = InvoiceFloatingIp.objects.filter(
            invoice=invoice,
            fip_id=fip_id
        ).exists()

        if not is_exists:
            # Get Price
            fip_price = FloatingIpsPrice.objects.first()

            # Create new invoice floating ip
            InvoiceFloatingIp.objects.create(
                invoice=invoice,
                fip_id=fip_id,
                ip=ip,
                current_state='allocated',
                start_date=timezone.now(),
                daily_price=fip_price.daily_price,
                monthly_price=fip_price.monthly_price,
            )

    @transaction.atomic
    def handle_delete(self, invoice: Invoice, payload):
        fip_id = payload['floatingip']['id']

        invoice_ip = FloatingIpsPrice.objects.filter(
            invoice=invoice,
            fip_id=fip_id,
        ).first()

        if invoice_ip:
            invoice_ip.end_date = timezone.now()
            invoice_ip.state = 'released'
            invoice_ip.save()
