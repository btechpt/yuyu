from core.component.base.event_handler import EventHandler


class InstanceEventHandler(EventHandler):
    def handle(self, event_type, raw_payload):
        if event_type == 'compute.instance.update':
            tenant_id = raw_payload['tenant_id']
            invoice = self.get_tenant_progress_invoice(tenant_id)

            is_updated = self.handle_update(invoice, event_type, raw_payload)

            if not is_updated and raw_payload['state'] == 'active':
                self.handle_create(invoice, event_type, raw_payload)

            if not is_updated and raw_payload['state'] == 'deleted':
                self.handle_delete(invoice, event_type, raw_payload)

    def clean_payload(self, event_type, raw_payload):
        payload = {
            "instance_id": raw_payload['instance_id'],
            "flavor_id": raw_payload['instance_flavor_id'],
            "name": raw_payload['display_name'],
        }

        return payload
