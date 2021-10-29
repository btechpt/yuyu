from core.component.base.event_handler import EventHandler
from core.component.floating_ips.invoice_handler import FloatingIpInvoiceHandler


class RouterEventHandler(EventHandler):
    def is_external_gateway_set(self, raw_payload):
        return raw_payload['router']['external_gateway_info'] is not None

    def handle(self, event_type, raw_payload):
        # Case: Creating router with external gateway
        if event_type == 'router.create.end' and self.is_external_gateway_set(raw_payload):
            tenant_id = raw_payload['router']['tenant_id']
            invoice = self.get_tenant_progress_invoice(tenant_id)
            self.handle_create(invoice, event_type, raw_payload)

        if event_type == 'router.update.end':
            tenant_id = raw_payload['router']['tenant_id']
            invoice = self.get_tenant_progress_invoice(tenant_id)

            # Handel update for existing instance
            self.handle_update(invoice, event_type, raw_payload)

            # Case: Existing router set gateway
            if self.is_external_gateway_set(raw_payload):
                self.handle_create(invoice, event_type, raw_payload)

            # Case: Existing router remove gateway
            if not self.is_external_gateway_set(raw_payload):
                self.handle_delete(invoice, event_type, raw_payload)

        # Case: Delete router
        if event_type == 'router.delete.end':
            tenant_id = raw_payload['router']['tenant_id']
            invoice = self.get_tenant_progress_invoice(tenant_id)
            self.handle_delete(invoice, event_type, raw_payload)

    def clean_payload(self, event_type, raw_payload):
        payload = {
            "router_id": raw_payload['router']['id'],
            "name": raw_payload['router']['name'],
        }

        return payload
