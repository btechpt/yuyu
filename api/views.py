from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
import dateutil.parser

from api.serializers import FlavorPriceSerializer, FloatingIpsPriceSerializer, VolumePriceSerializer, InvoiceSerializer, \
    SimpleInvoiceSerializer
from core.models import FlavorPrice, FloatingIpsPrice, VolumePrice, Invoice, BillingProject, InvoiceInstance, \
    InvoiceFloatingIp


class FlavorPriceViewSet(viewsets.ModelViewSet):
    queryset = FlavorPrice.objects
    serializer_class = FlavorPriceSerializer


class FloatingIpsPriceViewSet(viewsets.ModelViewSet):
    queryset = FloatingIpsPrice.objects
    serializer_class = FloatingIpsPriceSerializer


class VolumePriceViewSet(viewsets.ModelViewSet):
    queryset = VolumePrice.objects
    serializer_class = VolumePriceSerializer


class InvoiceViewSet(viewsets.ModelViewSet):
    serializer_class = InvoiceSerializer

    def get_queryset(self):
        tenant_id = self.request.query_params.get('tenant_id', None)
        return Invoice.objects.filter(project__tenant_id=tenant_id).order_by('-start_date')

    @action(detail=False)
    def simple_list(self, request):
        serializer = SimpleInvoiceSerializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['POST'])
    def init_invoice(self, request):
        project, created = BillingProject.objects.get_or_create(tenant_id=request.data['tenant_id'])

        date_today = timezone.now()
        month_first_day = date_today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        new_invoice = Invoice.objects.create(
            project=project,
            start_date=month_first_day,
            state=Invoice.InvoiceState.IN_PROGRESS
        )
        new_invoice.save()

        # Create Instance
        for instance in request.data['instances']:
            # Get Price
            flavor_price = FlavorPrice.objects.filter(flavor_id=instance['flavor_id']).first()

            # Create new invoice instance
            start_date = dateutil.parser.isoparse(instance['start_date'])
            if start_date < month_first_day:
                start_date = month_first_day
            InvoiceInstance.objects.create(
                invoice=new_invoice,
                instance_id=instance['instance_id'],
                name=instance['name'],
                flavor_id=instance['flavor_id'],
                current_state=instance['current_state'],
                start_date=start_date,
                daily_price=flavor_price.daily_price,
                monthly_price=flavor_price.monthly_price,
            )

        for fip in request.data['floating_ips']:
            # Get Price
            fip_price = FloatingIpsPrice.objects.first()

            # Create new invoice floating ip
            start_date = dateutil.parser.isoparse(fip['start_date'])
            if start_date < month_first_day:
                start_date = month_first_day
            InvoiceFloatingIp.objects.create(
                invoice=new_invoice,
                fip_id=fip['fip_id'],
                ip=fip['ip'],
                current_state=fip['current_state'],
                start_date=start_date,
                daily_price=fip_price.daily_price,
                monthly_price=fip_price.monthly_price,
            )

        serializer = InvoiceSerializer(new_invoice)

        return Response(serializer.data)
