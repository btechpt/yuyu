from django.conf import settings
import logging
import os
import signal
import time

from oslo_config import cfg
import oslo_messaging as messaging
from oslo_messaging import notify  # noqa

from django.core.management.base import BaseCommand

from core.event_endpoint import EventEndpoint

LOG = logging.getLogger("yuyu_notification")


class SignalExit(SystemExit):
    def __init__(self, signo, exccode=1):
        super(SignalExit, self).__init__(exccode)
        self.signo = signo


class Command(BaseCommand):
    help = 'Start Yuyu Event Monitor'

    def signal_handler(self, signum, frame):
        raise SignalExit(signum)

    def run_server(self, transport, server):
        try:
            server.start()
            server.wait()
            LOG.info('The server is terminating')
            time.sleep(1)
        except SignalExit as e:
            LOG.info('Signal %s is caught. Interrupting the execution',
                     e.signo)
            server.stop()
            server.wait()
        finally:
            transport.cleanup()

    def notify_server(self, transport, topics):
        endpoints = [EventEndpoint()]
        targets = list(map(lambda t: messaging.Target(topic=t), topics))
        server = notify.get_notification_listener(
            transport,
            targets,
            endpoints,
            executor='threading'
        )
        self.run_server(transport, server)

    def handle(self, *args, **options):
        url = settings.YUYU_NOTIFICATION_URL
        transport = messaging.get_notification_transport(cfg.CONF,
                                                         url=url)

        # oslo.config defaults
        cfg.CONF.heartbeat_interval = 5
        cfg.CONF.prog = os.path.basename(__file__)
        cfg.CONF.project = 'yuyu'

        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)

        self.notify_server(
            transport=transport,
            topics=settings.YUYU_NOTIFICATION_TOPICS,
        )
