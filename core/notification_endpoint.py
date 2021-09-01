import logging

from oslo_messaging import NotificationResult

from core.notification_handler.compute_handler import ComputeHandler
from core.notification_handler.network_handler import NetworkHandler
from core.notification_handler.volume_handler import VolumeHandler

LOG = logging.getLogger("rintik_notification")


class NotifyEndpoint(object):
    handlers = [
        ComputeHandler(),
        NetworkHandler(),
        VolumeHandler()
    ]

    def info(self, ctxt, publisher_id, event_type, payload, metadata):
        LOG.info("=== Event Received ===")
        LOG.info("Event Type: " + str(event_type))
        LOG.info("Payload: " + str(payload))

        # TODO: Error Handling
        for handler in self.handlers:
            handler.handle(event_type, payload)

        return NotificationResult.HANDLED
