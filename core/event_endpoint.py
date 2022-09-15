import logging
import traceback

from oslo_messaging import NotificationResult

from core.component import component
from core.component.project.event_handler import ProjectEventHandler
from core.notification import send_notification
from core.utils.dynamic_setting import get_dynamic_settings, BILLING_ENABLED, get_dynamic_setting
from yuyu import settings

LOG = logging.getLogger("yuyu_notification")


class EventEndpoint(object):
    def __init__(self):
        self.event_handler = [
            cls(component.INVOICE_HANDLER[label]) for label, cls in component.EVENT_HANDLER.items()
        ]

        # Add handler for project event
        self.event_handler.append(ProjectEventHandler())

    def info(self, ctxt, publisher_id, event_type, payload, metadata):
        LOG.info("=== Event Received ===")
        LOG.info("Event Type: " + str(event_type))
        LOG.info("Payload: " + str(payload))

        if not get_dynamic_setting(BILLING_ENABLED):
            return NotificationResult.HANDLED

        try:
            for handler in self.event_handler:
                handler.handle(event_type, payload)
        except Exception:
            send_notification(
                project=None,
                title=f'{settings.EMAIL_TAG} [Error] Error when handling OpenStack Notification',
                short_description=f'There is an error when handling OpenStack Notification',
                content=f'There is an error when handling OpenStack Notification \n {traceback.format_exc()}',
            )
        return NotificationResult.HANDLED
