from django.urls import path, include
from rest_framework import routers

from api import views
from core.component import component

router = routers.DefaultRouter()
for name, model in component.PRICE_MODEL.items():
    router.register(f"price/{name}", views.get_generic_model_view_set(model))

router.register(r'settings', views.DynamicSettingViewSet, basename='settings')
router.register(r'invoice', views.InvoiceViewSet, basename='invoice')
router.register(r'admin_overview', views.AdminOverviewViewSet, basename='admin_overview')
router.register(r'project_overview', views.ProjectOverviewViewSet, basename='project_overview')

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
]
