import logging

from oslo_messaging import NotificationResult

from core.notification_handler.compute_handler import ComputeHandler

LOG = logging.getLogger("rintik_notification")


class NotifyEndpoint(object):

    def info(self, ctxt, publisher_id, event_type, payload, metadata):
        # LOG.info("=== Event Received ===")
        # LOG.info("Event Type: " + str(event_type))
        # LOG.info("Payload: " + str(payload))

        ComputeHandler().handle(event_type, payload)

        return NotificationResult.HANDLED