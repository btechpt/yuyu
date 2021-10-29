from core.component.base.event_handler import EventHandler
from core.component.floating_ips.invoice_handler import FloatingIpInvoiceHandler


class SnapshotEventHandler(EventHandler):
    def handle(self, event_type, raw_payload):
        if event_type == 'snapshot.create.end':
            tenant_id = raw_payload['tenant_id']
            invoice = self.get_tenant_progress_invoice(tenant_id)
            self.handle_create(invoice, event_type, raw_payload)

        if event_type == 'snapshot.delete.end':
            tenant_id = raw_payload['tenant_id']
            invoice = self.get_tenant_progress_invoice(tenant_id)
            self.handle_delete(invoice, event_type, raw_payload)

        if event_type == 'snapshot.update.end':
            tenant_id = raw_payload['tenant_id']
            invoice = self.get_tenant_progress_invoice(tenant_id)
            self.handle_update(invoice, event_type, raw_payload)

    def clean_payload(self, event_type, raw_payload):
        payload = {
            "snapshot_id": raw_payload['snapshot_id'],
            "space_allocation_gb": raw_payload['volume_size'],
            "name": raw_payload['display_name'],
        }

        return payload
