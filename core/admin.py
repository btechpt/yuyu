from django.contrib import admin

from core.models import FlavorPrice, VolumePrice, FloatingIpsPrice, BillingProject, Invoice, InvoiceVolume, \
    InvoiceFloatingIp, InvoiceInstance


@admin.register(FlavorPrice)
class FlavorPriceAdmin(admin.ModelAdmin):
    list_display = ('flavor_id', 'daily_price', 'monthly_price')


@admin.register(FloatingIpsPrice)
class FloatingIpsPriceAdmin(admin.ModelAdmin):
    list_display = ('daily_price', 'monthly_price')


@admin.register(VolumePrice)
class VolumePriceAdmin(admin.ModelAdmin):
    list_display = ('volume_type_id', 'daily_price', 'monthly_price')


@admin.register(BillingProject)
class BillingProjectAdmin(admin.ModelAdmin):
    list_display = ('tenant_id',)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('__str__',)


@admin.register(InvoiceInstance)
class InvoiceInstanceAdmin(admin.ModelAdmin):
    list_display = ('instance_id',)


@admin.register(InvoiceFloatingIp)
class InvoiceFloatingIpAdmin(admin.ModelAdmin):
    list_display = ('fip_id',)


@admin.register(InvoiceVolume)
class InvoiceVolumeAdmin(admin.ModelAdmin):
    list_display = ('volume_id',)
