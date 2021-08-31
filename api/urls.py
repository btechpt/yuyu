from django.urls import path, include
from rest_framework import routers

from api import views

router = routers.DefaultRouter()
router.register(r'flavor_price', views.FlavorPriceViewSet)
router.register(r'floating_ips_price', views.FloatingIpsPriceViewSet)
router.register(r'volume_price', views.VolumePriceViewSet)
router.register(r'invoice', views.InvoiceViewSet, basename='invoice')

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
]
