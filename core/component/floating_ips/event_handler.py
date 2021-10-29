from core.component.base.event_handler import EventHandler
from core.component.floating_ips.invoice_handler import FloatingIpInvoiceHandler


class FloatingIpEventHandler(EventHandler):
    def handle(self, event_type, raw_payload):
        if event_type == 'floatingip.create.end':
            tenant_id = raw_payload['floatingip']['tenant_id']
            invoice = self.get_tenant_progress_invoice(tenant_id)
            self.handle_create(invoice, event_type, raw_payload)

        if event_type == 'floatingip.delete.end':
            tenant_id = raw_payload['floatingip']['tenant_id']
            invoice = self.get_tenant_progress_invoice(tenant_id)
            self.handle_delete(invoice, event_type, raw_payload)

    def clean_payload(self, event_type, raw_payload):
        payload = {
            "fip_id": raw_payload['floatingip']['id'],
            "ip": raw_payload['floatingip']['floating_ip_address'],
        }

        return payload
