from typing import Dict, Iterable

import dateutil.parser
import pytz
from django.db import transaction
from django.utils import timezone
from djmoney.money import Money
from djmoney.settings import DEFAULT_CURRENCY
from rest_framework import viewsets, serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers import InvoiceSerializer, SimpleInvoiceSerializer, BillingProjectSerializer, NotificationSerializer
from core.component import component, labels
from core.component.component import INVOICE_COMPONENT_MODEL
from core.exception import PriceNotFound
from core.models import Invoice, BillingProject, Notification
from core.notification import send_notification_from_template
from core.utils.dynamic_setting import get_dynamic_settings, get_dynamic_setting, set_dynamic_setting, BILLING_ENABLED, \
    INVOICE_TAX, COMPANY_NAME, COMPANY_LOGO, COMPANY_ADDRESS
from core.utils.model_utils import InvoiceComponentMixin
from yuyu import settings


def get_generic_model_view_set(model):
    name = type(model).__name__
    meta_params = {
        "model": model,
        "fields": "__all__"
    }
    meta_class = type("Meta", (object,), meta_params)
    serializer_class = type(f"{name}Serializer", (serializers.ModelSerializer,), {"Meta": meta_class})

    view_set_params = {
        "model": model,
        "queryset": model.objects,
        "serializer_class": serializer_class
    }

    return type(f"{name}ViewSet", (viewsets.ModelViewSet,), view_set_params)


class DynamicSettingViewSet(viewsets.ViewSet):
    def list(self, request):
        return Response(get_dynamic_settings())

    def retrieve(self, request, pk=None):
        return Response({
            pk: get_dynamic_setting(pk)
        })

    def update(self, request, pk=None):
        set_dynamic_setting(pk, request.data['value'])
        return Response({
            pk: get_dynamic_setting(pk)
        })

    def partial_update(self, request, pk=None):
        set_dynamic_setting(pk, request.data['value'])
        return Response({
            pk: get_dynamic_setting(pk)
        })


class InvoiceViewSet(viewsets.ModelViewSet):
    serializer_class = InvoiceSerializer

    def get_queryset(self):
        tenant_id = self.request.query_params.get('tenant_id', None)
        return Invoice.objects.filter(project__tenant_id=tenant_id).order_by('-start_date')

    def parse_time(self, time):
        dt = dateutil.parser.isoparse(time)
        if not dt.tzinfo:
            return pytz.UTC.localize(dt=dt)

        return dt

    @action(detail=False)
    def simple_list(self, request):
        serializer = SimpleInvoiceSerializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['POST'])
    def enable_billing(self, request):
        try:
            self.handle_init_billing(request.data)
            return Response({
                "status": "success"
            })
        except PriceNotFound as e:
            return Response({
                "message": str(e.identifier) + " price not found. Please check price configuration"
            }, status=400)

    @action(detail=False, methods=['POST'])
    def disable_billing(self, request):
        set_dynamic_setting(BILLING_ENABLED, False)
        active_invoices = Invoice.objects.filter(state=Invoice.InvoiceState.IN_PROGRESS).all()
        for active_invoice in active_invoices:
            self._close_active_invoice(active_invoice, timezone.now(), get_dynamic_setting(INVOICE_TAX))

        return Response({
            "status": "success"
        })

    def _close_active_invoice(self, active_invoice: Invoice, close_date, tax_percentage):
        active_components_map: Dict[str, Iterable[InvoiceComponentMixin]] = {}

        for label in labels.INVOICE_COMPONENT_LABELS:
            active_components_map[label] = getattr(active_invoice, label).filter(end_date=None).all()

            # Close Invoice Component
            for active_component in active_components_map[label]:
                active_component.close(close_date)

        # Finish current invoice
        active_invoice.close(close_date, tax_percentage)

    @action(detail=False, methods=['POST'])
    def reset_billing(self, request):
        self.handle_reset_billing()
        return Response({
            "status": "success"
        })

    @transaction.atomic
    def handle_init_billing(self, data):
        set_dynamic_setting(BILLING_ENABLED, True)

        projects = {}
        invoices = {}

        date_today = timezone.now()
        month_first_day = date_today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        for name, handler in component.INVOICE_HANDLER.items():
            payloads = data[name]

            for payload in payloads:

                if payload['tenant_id'] not in projects:
                    project, created = BillingProject.objects.get_or_create(tenant_id=payload['tenant_id'])
                    projects[payload['tenant_id']] = project

                if payload['tenant_id'] not in invoices:
                    invoice = Invoice.objects.create(
                        project=projects[payload['tenant_id']],
                        start_date=month_first_day,
                        state=Invoice.InvoiceState.IN_PROGRESS
                    )
                    invoices[payload['tenant_id']] = invoice

                start_date = self.parse_time(payload['start_date'])
                if start_date < month_first_day:
                    start_date = month_first_day

                payload['start_date'] = start_date
                payload['invoice'] = invoices[payload['tenant_id']]

                # create not accepting tenant_id, delete it
                del payload['tenant_id']
                handler.create(payload, fallback_price=True)

    @transaction.atomic
    def handle_reset_billing(self):
        set_dynamic_setting(BILLING_ENABLED, False)

        BillingProject.objects.all().delete()
        for name, handler in component.INVOICE_HANDLER.items():
            handler.delete()

        for name, model in component.PRICE_MODEL.items():
            model.objects.all().delete()

    @action(detail=True)
    def finish(self, request, pk):
        invoice = Invoice.objects.filter(id=pk).first()
        if invoice.state == Invoice.InvoiceState.UNPAID:
            invoice.finish()

        send_notification_from_template(
            project=invoice.project,
            title=settings.EMAIL_TAG + f' Invoice #{invoice.id} has been Paid',
            short_description=f'Invoice is paid with total of {invoice.total}',
            template='invoice.html',
            context={
                'invoice': invoice,
                'company_name': get_dynamic_setting(COMPANY_NAME),
                'address': get_dynamic_setting(COMPANY_ADDRESS),
            }
        )

        serializer = InvoiceSerializer(invoice)
        return Response(serializer.data)

    @action(detail=True)
    def rollback_to_unpaid(self, request, pk):
        invoice = Invoice.objects.filter(id=pk).first()
        if invoice.state == Invoice.InvoiceState.FINISHED:
            invoice.rollback_to_unpaid()

        send_notification_from_template(
            project=invoice.project,
            title=settings.EMAIL_TAG + f' Invoice #{invoice.id} is Unpaid',
            short_description=f'Invoice is Unpaid with total of {invoice.total}',
            template='invoice.html',
            context={
                'invoice': invoice,
                'company_name': get_dynamic_setting(COMPANY_NAME),
                'address': get_dynamic_setting(COMPANY_ADDRESS),
            }
        )

        serializer = InvoiceSerializer(invoice)
        return Response(serializer.data)


class AdminOverviewViewSet(viewsets.ViewSet):
    def list(self, request):
        return Response({})

    @action(detail=False, methods=['GET'])
    def total_resource(self, request):
        data = {
            'label': [],
            'data': [],
        }
        for k, v in INVOICE_COMPONENT_MODEL.items():
            data['label'].append(k)
            data['data'].append(v.objects.filter(invoice__state=Invoice.InvoiceState.IN_PROGRESS).count())

        return Response(data)

    @action(detail=False, methods=['GET'])
    def active_resource(self, request):
        data = {
            'label': [],
            'data': [],
        }
        for k, v in INVOICE_COMPONENT_MODEL.items():
            data['label'].append(k)
            data['data'].append(
                v.objects.filter(invoice__state=Invoice.InvoiceState.IN_PROGRESS, end_date=None).count())

        return Response(data)

    @action(detail=False, methods=['GET'])
    def price_total_resource(self, request):
        data = {
            'label': [],
            'data': [],
        }
        for k, v in INVOICE_COMPONENT_MODEL.items():
            sum_of_price = sum([q.price_charged for q in
                                v.objects.filter(invoice__state=Invoice.InvoiceState.IN_PROGRESS).all()])

            sum_of_price = sum_of_price or Money(amount=0, currency=settings.DEFAULT_CURRENCY)
            data['label'].append(k + ' (' + str(sum_of_price.currency) + ')')
            data['data'].append(sum_of_price.amount)

        return Response(data)

    @action(detail=False, methods=['GET'])
    def price_active_resource(self, request):
        data = {
            'label': [],
            'data': [],
        }
        for k, v in INVOICE_COMPONENT_MODEL.items():
            sum_of_price = sum([q.price_charged for q in
                                v.objects.filter(invoice__state=Invoice.InvoiceState.IN_PROGRESS, end_date=None).all()])

            sum_of_price = sum_of_price or Money(amount=0, currency=settings.DEFAULT_CURRENCY)
            data['label'].append(k + ' (' + str(sum_of_price.currency) + ')')
            data['data'].append(sum_of_price.amount)

        return Response(data)


class ProjectOverviewViewSet(viewsets.ViewSet):
    def list(self, request):
        project = BillingProject.objects.all()
        serializer = BillingProjectSerializer(project, many=True)

        return Response(serializer.data)

    @action(detail=True, methods=['GET'])
    def get_tenant(self, request, pk):
        project = BillingProject.objects.filter(tenant_id=pk).first()
        serializer = BillingProjectSerializer(project)

        return Response(serializer.data)

    @action(detail=True, methods=['POST'])
    def update_email(self, request, pk):
        project = BillingProject.objects.filter(tenant_id=pk).first()
        serializer = BillingProjectSerializer(project, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "status": "success"
        })

    @action(detail=False, methods=['GET'])
    def total_resource(self, request):
        tenant_id = self.request.query_params.get('tenant_id', None)
        project = BillingProject.objects.filter(tenant_id=tenant_id).first()
        data = {
            'label': [],
            'data': [],
        }
        for k, v in INVOICE_COMPONENT_MODEL.items():
            data['label'].append(k)
            data['data'].append(
                v.objects.filter(invoice__project=project, invoice__state=Invoice.InvoiceState.IN_PROGRESS).count())

        return Response(data)

    @action(detail=False, methods=['GET'])
    def active_resource(self, request):
        tenant_id = self.request.query_params.get('tenant_id', None)
        project = BillingProject.objects.filter(tenant_id=tenant_id).first()
        data = {
            'label': [],
            'data': [],
        }
        for k, v in INVOICE_COMPONENT_MODEL.items():
            data['label'].append(k)
            data['data'].append(
                v.objects.filter(invoice__project=project, invoice__state=Invoice.InvoiceState.IN_PROGRESS,
                                 end_date=None).count())

        return Response(data)

    @action(detail=False, methods=['GET'])
    def price_total_resource(self, request):
        tenant_id = self.request.query_params.get('tenant_id', None)
        project = BillingProject.objects.filter(tenant_id=tenant_id).first()
        data = {
            'label': [],
            'data': [],
        }
        for k, v in INVOICE_COMPONENT_MODEL.items():
            sum_of_price = sum([q.price_charged for q in
                                v.objects.filter(invoice__project=project,
                                                 invoice__state=Invoice.InvoiceState.IN_PROGRESS).all()])

            sum_of_price = sum_of_price or Money(amount=0, currency=settings.DEFAULT_CURRENCY)
            data['label'].append(k + ' (' + str(sum_of_price.currency) + ')')
            data['data'].append(sum_of_price.amount)

        return Response(data)

    @action(detail=False, methods=['GET'])
    def price_active_resource(self, request):
        tenant_id = self.request.query_params.get('tenant_id', None)
        project = BillingProject.objects.filter(tenant_id=tenant_id).first()
        data = {
            'label': [],
            'data': [],
        }
        for k, v in INVOICE_COMPONENT_MODEL.items():
            sum_of_price = sum([q.price_charged for q in
                                v.objects.filter(invoice__project=project,
                                                 invoice__state=Invoice.InvoiceState.IN_PROGRESS, end_date=None).all()])

            sum_of_price = sum_of_price or Money(amount=0, currency=settings.DEFAULT_CURRENCY)
            data['label'].append(k + ' (' + str(sum_of_price.currency) + ')')
            data['data'].append(sum_of_price.amount)

        return Response(data)


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        tenant_id = self.request.query_params.get('tenant_id', None)
        if tenant_id is None:
            return Notification.objects.order_by('-created_at')
        if tenant_id == '0':
            return Notification.objects.filter(project=None).order_by('-created_at')

        return Notification.objects.filter(project__tenant_id=tenant_id).order_by('-created_at')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_read = True
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['GET'])
    def resend(self, request, pk):
        notification = Notification.objects.filter(id=pk).first()
        notification.send()

        serializer = NotificationSerializer(notification)

        return Response(serializer.data)

    @action(detail=True, methods=['GET'])
    def set_read(self, request, pk):
        notification = Notification.objects.filter(id=pk).first()
        notification.is_read = True
        notification.save()

        serializer = NotificationSerializer(notification)

        return Response(serializer.data)

    @action(detail=True, methods=['GET'])
    def set_unread(self, request, pk):
        notification = Notification.objects.filter(id=pk).first()
        notification.is_read = False
        notification.save()

        serializer = NotificationSerializer(notification)

        return Response(serializer.data)
