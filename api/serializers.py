from djmoney.contrib.django_rest_framework import MoneyField
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
    adjusted_end_date = serializers.DateTimeField()
    price_charged = MoneyField(max_digits=10, decimal_places=0)
    price_charged_currency = serializers.CharField(source="price_charged.currency")

    class Meta:
        model = InvoiceInstance
        fields = '__all__'


class InvoiceVolumeSerializer(serializers.ModelSerializer):
    adjusted_end_date = serializers.DateTimeField()
    price_charged = MoneyField(max_digits=10, decimal_places=0)
    price_charged_currency = serializers.CharField(source="price_charged.currency")

    class Meta:
        model = InvoiceVolume
        fields = '__all__'


class InvoiceFloatingIpSerializer(serializers.ModelSerializer):
    adjusted_end_date = serializers.DateTimeField()
    price_charged = MoneyField(max_digits=10, decimal_places=0)
    price_charged_currency = serializers.CharField(source="price_charged.currency")

    class Meta:
        model = InvoiceFloatingIp
        fields = '__all__'


class InvoiceSerializer(serializers.ModelSerializer):
    instances = InvoiceInstanceSerializer(many=True)
    floating_ips = InvoiceFloatingIpSerializer(many=True)
    volumes = InvoiceVolumeSerializer(many=True)
    subtotal = MoneyField(max_digits=10, decimal_places=0)
    subtotal_currency = serializers.CharField(source="subtotal.currency")

    class Meta:
        model = Invoice
        fields = '__all__'


class SimpleInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['id', 'start_date', 'end_date', 'state']

