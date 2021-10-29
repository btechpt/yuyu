from core.component.image.event_handler import ImageEventHandler
from core.component.image.invoice_handler import ImageInvoiceHandler
from core.component.router.event_handler import RouterEventHandler
from core.component.router.invoice_handler import RouterInvoiceHandler
from core.component.snapshot.event_handler import SnapshotEventHandler
from core.component.snapshot.invoice_handler import SnapshotInvoiceHandler
from core.models import InvoiceInstance, InvoiceVolume, InvoiceFloatingIp, FlavorPrice, FloatingIpsPrice, VolumePrice, \
    RouterPrice, SnapshotPrice, InvoiceRouter, InvoiceSnapshot, ImagePrice, InvoiceImage
from core.component.floating_ips.event_handler import FloatingIpEventHandler
from core.component.floating_ips.invoice_handler import FloatingIpInvoiceHandler
from core.component.instances.event_handler import InstanceEventHandler
from core.component.instances.invoice_handler import InstanceInvoiceHandler
from core.component.labels import LABEL_INSTANCES, LABEL_VOLUMES, LABEL_FLOATING_IPS, LABEL_ROUTERS, LABEL_SNAPSHOTS, \
    LABEL_IMAGES
from core.component.volume.event_handler import VolumeEventHandler
from core.component.volume.invoice_handler import VolumeInvoiceHandler

"""
Define a model that represent price for particular component
"""
PRICE_MODEL = {
    "flavor": FlavorPrice,
    "floating_ip": FloatingIpsPrice,
    "volume": VolumePrice,
    "router": RouterPrice,
    "snapshot": SnapshotPrice,
    "image": ImagePrice
}

"""
Define a model that represent a component in invoice.
The label that used for the key must be able to access through [Invoice] model
"""
INVOICE_COMPONENT_MODEL = {
    LABEL_INSTANCES: InvoiceInstance,
    LABEL_VOLUMES: InvoiceVolume,
    LABEL_FLOATING_IPS: InvoiceFloatingIp,
    LABEL_ROUTERS: InvoiceRouter,
    LABEL_SNAPSHOTS: InvoiceSnapshot,
    LABEL_IMAGES: InvoiceImage
}

"""
Define a class that handle the event from message queue
"""
EVENT_HANDLER = {
    LABEL_INSTANCES: InstanceEventHandler,
    LABEL_VOLUMES: VolumeEventHandler,
    LABEL_FLOATING_IPS: FloatingIpEventHandler,
    LABEL_ROUTERS: RouterEventHandler,
    LABEL_SNAPSHOTS: SnapshotEventHandler,
    LABEL_IMAGES: ImageEventHandler
}

"""
Define an instance that handle invoice creation or update
"""
INVOICE_HANDLER = {
    LABEL_INSTANCES: InstanceInvoiceHandler(),
    LABEL_VOLUMES: VolumeInvoiceHandler(),
    LABEL_FLOATING_IPS: FloatingIpInvoiceHandler(),
    LABEL_ROUTERS: RouterInvoiceHandler(),
    LABEL_SNAPSHOTS: SnapshotInvoiceHandler(),
    LABEL_IMAGES: ImageInvoiceHandler()
}
