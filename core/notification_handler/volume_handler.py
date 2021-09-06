from django.db import transaction
from django.utils import timezone

from core.models import Invoice, InvoiceVolume, VolumePrice


class VolumeHandler:
    def get_tenant_progress_invoice(self, tenant_id):
        return Invoice.objects.filter(project__tenant_id=tenant_id, state=Invoice.InvoiceState.IN_PROGRESS).first()

    def handle(self, event_type, payload):
        if event_type == 'volume.create.end':
            tenant_id = payload['tenant_id']

            # Get instance invoice
            invoice = self.get_tenant_progress_invoice(tenant_id)
            if not invoice:
                return

            self.handle_create(invoice, payload)

        if event_type == 'volume.delete.end':
            tenant_id = payload['tenant_id']

            # Get instance invoice
            invoice = self.get_tenant_progress_invoice(tenant_id)
            if not invoice:
                return

            self.handle_delete(invoice, payload)

    @transaction.atomic
    def handle_create(self, invoice: Invoice, payload):
        volume_id = payload['volume_id']
        volume_type_id = payload['volume_type']
        name = payload['display_name']
        status = payload['status']
        size = payload['size']

        # TODO: More filter if update is implemented
        is_exists = InvoiceVolume.objects.filter(
            invoice=invoice,
            volume_id=volume_id
        ).exists()

        if not is_exists:
            # Get Price
            volume_price = VolumePrice.objects.filter(volume_type_id=volume_type_id).first()

            # Create new invoice floating ip
            InvoiceVolume.objects.create(
                invoice=invoice,
                volume_id=volume_id,
                volume_name=name,
                volume_type_id=volume_type_id,
                space_allocation_gb=size,
                current_state=status,
                start_date=timezone.now(),
                daily_price=volume_price.daily_price,
                monthly_price=volume_price.monthly_price,
            )

    @transaction.atomic
    def handle_delete(self, invoice: Invoice, payload):
        volume_id = payload['volume_id']
        status = payload['status']

        # TODO: More filter if update is implemented
        invoice_volume = InvoiceVolume.objects.filter(
            invoice=invoice,
            volume_id=volume_id
        ).first()

        if invoice_volume:
            invoice_volume.end_date = timezone.now()
            invoice_volume.current_state = status
            invoice_volume.save()
