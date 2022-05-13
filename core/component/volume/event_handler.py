from core.component.base.event_handler import EventHandler


class VolumeEventHandler(EventHandler):
    def handle(self, event_type, raw_payload):
        if event_type == 'volume.create.end':
            tenant_id = raw_payload['tenant_id']
            invoice = self.get_tenant_progress_invoice(tenant_id)
            self.handle_create(invoice, event_type, raw_payload)

        if event_type == 'volume.delete.end':
            tenant_id = raw_payload['tenant_id']
            invoice = self.get_tenant_progress_invoice(tenant_id)
            self.handle_delete(invoice, event_type, raw_payload)

        if event_type in ['volume.resize.end', 'volume.update.end', 'volume.retype']:
            tenant_id = raw_payload['tenant_id']
            invoice = self.get_tenant_progress_invoice(tenant_id)
            self.handle_update(invoice, event_type, raw_payload)

    def clean_payload(self, event_type, raw_payload):
        payload = {
            "volume_id": raw_payload['volume_id'],
            "volume_type_id": raw_payload['volume_type'],
            "volume_name": raw_payload['display_name'] or raw_payload['volume_id'],
            "space_allocation_gb": raw_payload['size'],
        }

        return payload
