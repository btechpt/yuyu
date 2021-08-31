from django.utils import timezone

from core.models import Invoice, InvoiceInstance, FlavorPrice


class ComputeHandler:
    def get_tenant_progress_invoice(self, tenant_id):
        return Invoice.objects.filter(project_tenant_id=tenant_id, state=Invoice.InvoiceState.IN_PROGRESS).first()

    def handle(self, event_type, payload):
        if event_type == 'compute.instance.update':
            tenant_id = payload['tenant_id']

            # Get instance invoice
            invoice = self.get_tenant_progress_invoice(tenant_id)
            if not invoice:
                return

            # print('New Compute State: ' + str(payload['state']))
            if payload['state'] == 'active':
                self.handle_active_state(invoice, payload)

            if payload['state'] == 'deleted':
                self.handle_delete_state(invoice, payload)

            # TODO: Handle flavor change

    def handle_active_state(self, invoice, payload):
        display_name = payload['display_name']
        instance_id = payload['instance_id']
        flavor_id = payload['instance_flavor_id']
        state = payload['state']

        is_exists = InvoiceInstance.objects.filter(
            invoice=invoice,
            instance_id=instance_id,
            flavor_id=flavor_id
        ).exists()

        if not is_exists:
            # Get Price
            flavor_price = FlavorPrice.objects.filter(flavor_id=flavor_id).first()

            # Create new invoice instance
            InvoiceInstance.objects.create(
                invoice=invoice,
                instance_id=instance_id,
                name=display_name,
                flavor_id=flavor_id,
                current_state=state,
                start_date=timezone.now(),
                daily_price=flavor_price.daily_price,
                monthly_price=flavor_price.monthly_price,
            )

    def handle_delete_state(self, invoice, payload):
        instance_id = payload['instance_id']
        flavor_id = payload['instance_flavor_id']
        state = payload['state']

        invoice_instance = InvoiceInstance.objects.filter(
            invoice=invoice,
            instance_id=instance_id,
            flavor_id=flavor_id,
            state=state
        ).first()

        if invoice_instance:
            invoice_instance.end_date = timezone.now()
            invoice_instance.state = state
            invoice_instance.save()
