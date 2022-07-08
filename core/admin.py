from django.contrib import admin

from core.models import FlavorPrice, VolumePrice, FloatingIpsPrice, BillingProject, Invoice, InvoiceVolume, \
    InvoiceFloatingIp, InvoiceInstance, DynamicSetting, InvoiceImage, ImagePrice, SnapshotPrice, RouterPrice, \
    InvoiceSnapshot, InvoiceRouter, Notification


@admin.register(DynamicSetting)
class FlavorPriceAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'type')


@admin.register(FlavorPrice)
class FlavorPriceAdmin(admin.ModelAdmin):
    list_display = ('flavor_id', 'hourly_price', 'monthly_price')


@admin.register(FloatingIpsPrice)
class FloatingIpsPriceAdmin(admin.ModelAdmin):
    list_display = ('hourly_price', 'monthly_price')


@admin.register(VolumePrice)
class VolumePriceAdmin(admin.ModelAdmin):
    list_display = ('volume_type_id', 'hourly_price', 'monthly_price')


@admin.register(RouterPrice)
class RouterPriceAdmin(admin.ModelAdmin):
    list_display = ('hourly_price', 'monthly_price')


@admin.register(SnapshotPrice)
class SnapshotPriceAdmin(admin.ModelAdmin):
    list_display = ('hourly_price', 'monthly_price')


@admin.register(ImagePrice)
class ImagePriceAdmin(admin.ModelAdmin):
    list_display = ('hourly_price', 'monthly_price')


@admin.register(BillingProject)
class BillingProjectAdmin(admin.ModelAdmin):
    list_display = ('tenant_id',)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'project', 'start_date')


@admin.register(InvoiceInstance)
class InvoiceInstanceAdmin(admin.ModelAdmin):
    list_display = ('instance_id',)


@admin.register(InvoiceFloatingIp)
class InvoiceFloatingIpAdmin(admin.ModelAdmin):
    list_display = ('fip_id',)


@admin.register(InvoiceVolume)
class InvoiceVolumeAdmin(admin.ModelAdmin):
    list_display = ('volume_id',)


@admin.register(InvoiceRouter)
class InvoiceRouterAdmin(admin.ModelAdmin):
    list_display = ('router_id', 'name')


@admin.register(InvoiceSnapshot)
class InvoiceSnapshotAdmin(admin.ModelAdmin):
    list_display = ('snapshot_id', 'name', 'space_allocation_gb')


@admin.register(InvoiceImage)
class InvoiceImageAdmin(admin.ModelAdmin):
    list_display = ('image_id', 'name', 'space_allocation_gb')


@admin.register(Notification)
class InvoiceImageAdmin(admin.ModelAdmin):
    list_display = ('project', 'title', 'short_description', 'sent_status')
