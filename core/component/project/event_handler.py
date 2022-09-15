import logging

from core.models import BillingProject

LOG = logging.getLogger("yuyu_notification")


class ProjectEventHandler:
    def handle(self, event_type, raw_payload):
        if event_type == 'identity.project.created':
            new_project_id = raw_payload['target']['id']
            LOG.info("Registering new project " + new_project_id)
            project = BillingProject()
            project.tenant_id = new_project_id
            project.save()
