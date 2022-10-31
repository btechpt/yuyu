import logging

from core.models import BillingProject, Invoice
from django.utils import timezone

LOG = logging.getLogger("yuyu_notification")


class ProjectEventHandler:
    def handle(self, event_type, raw_payload):
        if event_type == 'identity.project.created':
            new_project_id = raw_payload['target']['id']
            LOG.info("Registering new project " + new_project_id)
            project = BillingProject()
            project.tenant_id = new_project_id
            project.save()
            LOG.info("Creating invoice for " + new_project_id)
            self.init_first_invoice(project)

    def init_first_invoice(self, project):
        date_today = timezone.now()
        month_first_day = date_today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        Invoice.objects.create(
            project=project,
            start_date=month_first_day,
            state=Invoice.InvoiceState.IN_PROGRESS
        )
