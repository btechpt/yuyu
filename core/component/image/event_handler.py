from core.component.base.event_handler import EventHandler


class ImageEventHandler(EventHandler):
    def handle(self, event_type, raw_payload):
        if event_type == 'image.activate':
            tenant_id = raw_payload['owner']
            invoice = self.get_tenant_progress_invoice(tenant_id)
            self.handle_create(invoice, event_type, raw_payload)

        if event_type == 'image.delete':
            tenant_id = raw_payload['owner']
            invoice = self.get_tenant_progress_invoice(tenant_id)
            self.handle_delete(invoice, event_type, raw_payload)

        if event_type == 'image.update':
            tenant_id = raw_payload['owner']
            invoice = self.get_tenant_progress_invoice(tenant_id)
            self.handle_update(invoice, event_type, raw_payload)

    def clean_payload(self, event_type, raw_payload):
        payload = {
            "image_id": raw_payload['id'],
            "space_allocation_gb": raw_payload['size'] / 1024 / 1024 / 1024,
            "name": raw_payload['name'] or raw_payload['id'],
        }

        return payload
