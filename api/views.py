from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers import FlavorPriceSerializer, FloatingIpsPriceSerializer, VolumePriceSerializer, InvoiceSerializer, \
    SimpleInvoiceSerializer
from core.models import FlavorPrice, FloatingIpsPrice, VolumePrice, Invoice


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
        return Invoice.objects.filter(project__tenant_id=tenant_id)

    @action(detail=False)
    def simple_lists(self, request):
        serializer = SimpleInvoiceSerializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['POST'])
    def init_invoice(self, request):
        # TODO: Init invoice
        serializer = InvoiceSerializer()
        return Response(serializer.data)
