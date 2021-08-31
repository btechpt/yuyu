from rest_framework import serializers

from core.models import FlavorPrice, VolumePrice, FloatingIpsPrice, Invoice, InvoiceInstance, InvoiceVolume, \
    InvoiceFloatingIp


class FlavorPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlavorPrice
        fields = '__all__'


class FloatingIpsPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FloatingIpsPrice
        fields = '__all__'


class VolumePriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = VolumePrice
        fields = '__all__'


class InvoiceInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceInstance
        fields = '__all__'


class InvoiceVolumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceVolume
        fields = '__all__'


class InvoiceFloatingIpSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceFloatingIp
        fields = '__all__'


class InvoiceSerializer(serializers.ModelSerializer):
    instances = InvoiceInstanceSerializer(many=True)
    floating_ips = InvoiceFloatingIpSerializer(many=True)
    volumes = InvoiceVolumeSerializer(many=True)

    class Meta:
        model = Invoice
        fields = '__all__'


class SimpleInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'

