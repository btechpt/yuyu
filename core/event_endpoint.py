import logging

from oslo_messaging import NotificationResult

from core.component import component
from core.utils.dynamic_setting import get_dynamic_settings, BILLING_ENABLED, get_dynamic_setting

LOG = logging.getLogger("rintik_notification")


class EventEndpoint(object):
    def __init__(self):
        self.event_handler = [
            cls(component.INVOICE_HANDLER[label]) for label, cls in component.EVENT_HANDLER.items()
        ]

    def info(self, ctxt, publisher_id, event_type, payload, metadata):
        LOG.info("=== Event Received ===")
        LOG.info("Event Type: " + str(event_type))
        LOG.info("Payload: " + str(payload))

        if not get_dynamic_setting(BILLING_ENABLED):
            return NotificationResult.HANDLED

        # TODO: Error Handling
        for handler in self.event_handler:
            handler.handle(event_type, payload)

        return NotificationResult.HANDLED
