"""API views for the InventoryOne Broker Web App."""
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Count, Q
from django.http import FileResponse, HttpResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from .models import (
    AuditLog,
    Booking,
    Broker,
    Commission,
    CompanyProfile,
    Customer,
    Document,
    Notification,
    OTPCode,
    Plot,
    Project,
    SupportTicket,
)
from .serializers import (
    AuditLogSerializer,
    BookingSerializer,
    BrokerSerializer,
    BulkPlotSerializer,
    CommissionSerializer,
    CompanyProfileSerializer,
    CustomerSerializer,
    DocumentSerializer,
    NotificationSerializer,
    PlotWriteSerializer,
    ProjectDetailSerializer,
    ProjectListSerializer,
    ProjectWriteSerializer,
    SupportTicketSerializer,
)
from .services import audit, documents, notifications

TDS_PCT = Decimal(10)


def get_broker(request):
    """Return the Broker profile of the authenticated user."""
    return Broker.objects.select_related('user').get(user=request.user)


def project_counts(project):
    counts = project.plots.aggregate(
        total=Count('id'),
        available=Count('id', filter=Q(status=Plot.STATUS_AVAILABLE)),
        on_hold=Count('id', filter=Q(status=Plot.STATUS_ON_HOLD)),
        sold=Count('id', filter=Q(status=Plot.STATUS_SOLD)),
    )
    return {
        'total_plots': counts['total'] or 0,
        'available': counts['available'] or 0,
        'on_hold': counts['on_hold'] or 0,
        'sold': counts['sold'] or 0,
    }


def push_plot_update(plot, status_value):
    """Broadcast a plot status change to live dashboards."""
    from .consumers import broadcast_inventory_sync

    broadcast_inventory_sync(
        project_id=plot.project_id,
        plot_id=plot.id,
        status=status_value,
        counts=project_counts(plot.project),
    )


# ---------------------------------------------------------------------------
# Authentication (OTP)
# ---------------------------------------------------------------------------

@api_view(['POST'])
@permission_classes([AllowAny])
def request_otp(request):
    email = (request.data.get('email') or '').strip().lower()
    if not email:
        return Response({'detail': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

    user, created = User.objects.get_or_create(
        username=email,
        defaults={'email': email, 'first_name': email.split('@')[0].title()},
    )
    broker, _ = Broker.objects.get_or_create(user=user)

    otp = OTPCode.generate_for(email)
    payload = {
        'detail': 'OTP sent to your registered email.',
        'email': email,
        'is_new_broker': created,
        'broker_id': broker.id,
    }
    if settings.OTP_DEBUG_MODE:
        # Mail delivery is stubbed in development; surface the code.
        payload['dev_code'] = otp.code
    return Response(payload, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    email = (request.data.get('email') or '').strip().lower()
    code = (request.data.get('code') or '').strip()

    otp = OTPCode.objects.filter(email=email, code=code).first()
    if not otp or not otp.is_valid:
        return Response({'detail': 'Invalid or expired OTP.'}, status=status.HTTP_400_BAD_REQUEST)
    otp.delete()

    user = User.objects.filter(username=email).first()
    if user is None:
        return Response({'detail': 'No account found for this email.'},
                        status=status.HTTP_404_NOT_FOUND)

    broker, _ = Broker.objects.get_or_create(user=user)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({
        'token': token.key,
        'role': 'admin' if user.is_staff else 'broker',
        'is_staff': user.is_staff,
        'broker': BrokerSerializer(broker).data,
    })


# ---------------------------------------------------------------------------
# Broker profile / KYC
# ---------------------------------------------------------------------------

@api_view(['GET', 'PATCH'])
def me(request):
    broker = get_broker(request)
    if request.method == 'GET':
        return Response(BrokerSerializer(broker).data)

    serializer = BrokerSerializer(broker, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    audit.log_action(request.user, 'profile.updated', 'Broker', broker.id)
    return Response(serializer.data)


# ---------------------------------------------------------------------------
# Projects & inventory
# ---------------------------------------------------------------------------

def annotated_projects():
    return Project.objects.annotate(
        total_plots=Count('plots'),
        available=Count('plots', filter=Q(plots__status=Plot.STATUS_AVAILABLE)),
        on_hold=Count('plots', filter=Q(plots__status=Plot.STATUS_ON_HOLD)),
        sold=Count('plots', filter=Q(plots__status=Plot.STATUS_SOLD)),
    )


@api_view(['GET'])
def project_list(request):
    projects = annotated_projects().filter(status=Project.STATUS_ACTIVE)
    return Response(ProjectListSerializer(projects, many=True).data)


@api_view(['GET'])
def project_detail(request, pk):
    project = Project.objects.filter(pk=pk).first()
    if project is None:
        return Response({'detail': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)
    project = annotated_projects().filter(pk=project.pk).first()
    return Response(ProjectDetailSerializer(project).data)


# ---------------------------------------------------------------------------
# Customers
# ---------------------------------------------------------------------------

@api_view(['GET', 'POST'])
def customers(request):
    broker = get_broker(request)
    if request.method == 'GET':
        return Response(CustomerSerializer(broker.customers.all(), many=True).data)

    serializer = CustomerSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(broker=broker)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


# ---------------------------------------------------------------------------
# Bookings
# ---------------------------------------------------------------------------

@api_view(['GET', 'POST'])
def bookings(request):
    broker = get_broker(request)
    if request.method == 'GET':
        qs = broker.bookings.select_related('plot', 'plot__project', 'customer')
        return Response(BookingSerializer(qs, many=True).data)

    serializer = BookingSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    with transaction.atomic():
        plot = Plot.objects.select_for_update().get(pk=serializer.validated_data['plot'].pk)
        if plot.status != Plot.STATUS_AVAILABLE:
            return Response({'detail': 'That plot is no longer available.'},
                            status=status.HTTP_409_CONFLICT)

        booking = serializer.save(broker=broker, status=Booking.STATUS_PENDING)
        plot.status = Plot.STATUS_ON_HOLD
        plot.save(update_fields=['status'])

    push_plot_update(plot, plot.status)
    notifications.notify(
        broker,
        title='Booking request submitted',
        body=f'Plot {plot.plot_number} at {plot.project.name} is on hold pending approval.',
        kind=Notification.KIND_BOOKING,
        link='/bookings',
    )
    audit.log_action(request.user, 'booking.created', 'Booking', booking.id,
                     plot=plot.plot_number, token_amount=str(booking.token_amount))
    return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)


# ---------------------------------------------------------------------------
# Commissions
# ---------------------------------------------------------------------------

@api_view(['GET'])
def commissions(request):
    broker = get_broker(request)
    qs = Commission.objects.filter(broker=broker).select_related(
        'booking__plot', 'booking__customer', 'booking__plot__project')
    return Response(CommissionSerializer(qs, many=True).data)


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------

@api_view(['GET'])
def notification_list(request):
    broker = get_broker(request)
    qs = broker.notifications.all()
    unread_only = request.query_params.get('unread')
    if unread_only in ('1', 'true', 'True'):
        qs = qs.filter(read=False)
    return Response(NotificationSerializer(qs, many=True).data)


@api_view(['GET'])
def notification_unread_count(request):
    broker = get_broker(request)
    return Response({'unread': broker.notifications.filter(read=False).count()})


@api_view(['POST'])
def notification_mark_read(request):
    broker = get_broker(request)
    ids = request.data.get('ids')
    qs = broker.notifications.all()
    if ids:
        qs = qs.filter(id__in=ids)
    else:
        qs = qs.filter(read=False)
    updated = qs.update(read=True)
    return Response({'marked_read': updated})


# ---------------------------------------------------------------------------
# Support tickets
# ---------------------------------------------------------------------------

@api_view(['GET', 'POST'])
def tickets(request):
    broker = get_broker(request)
    if request.method == 'GET':
        return Response(SupportTicketSerializer(broker.tickets.all(), many=True).data)

    serializer = SupportTicketSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    ticket = serializer.save(broker=broker)
    audit.log_action(request.user, 'ticket.created', 'SupportTicket', ticket.id,
                     subject=ticket.subject)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def company_profile(request):
    """Public contact details and the relationship manager."""
    return Response(CompanyProfileSerializer(CompanyProfile.load()).data)


# ---------------------------------------------------------------------------
# Documents
# ---------------------------------------------------------------------------

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def document_list(request):
    """List documents. Brokers see their own KYC files plus public downloads."""
    if request.user.is_authenticated:
        broker = get_broker(request)
        qs = Document.objects.filter(broker=broker)
    else:
        qs = Document.objects.none()

    kind = request.query_params.get('kind')
    if kind == 'price_list':
        qs = Document.objects.filter(kind=Document.PRICE_LIST)
    elif kind == 'form':
        qs = Document.objects.filter(kind=Document.FORM)
    elif kind:
        qs = qs.filter(kind=kind)

    if request.method == 'POST':
        broker = get_broker(request)
        kind = request.data.get('kind')
        upload = request.FILES.get('file')
        if kind not in Document.KYC_KINDS:
            return Response({'detail': f'kind must be one of {Document.KYC_KINDS}'},
                            status=status.HTTP_400_BAD_REQUEST)
        if not upload:
            return Response({'detail': 'A file is required.'}, status=status.HTTP_400_BAD_REQUEST)

        title = request.data.get('title') or f'{dict(Document.KIND_CHOICES).get(kind, kind)}'
        doc = Document(
            broker=broker,
            kind=kind,
            title=title,
            content_type=upload.content_type or 'application/octet-stream',
            size_bytes=upload.size,
        )
        doc.file.save(upload.name, upload, save=False)
        doc.save()

        audit.log_action(request.user, 'kyc.document.uploaded', 'Document', doc.id, kind=kind)
        return Response(DocumentSerializer(doc, context={'request': request}).data,
                        status=status.HTTP_201_CREATED)

    return Response(DocumentSerializer(qs, many=True).data)


@api_view(['DELETE'])
def document_delete(request, pk):
    broker = get_broker(request)
    doc = Document.objects.filter(pk=pk, broker=broker).first()
    if doc is None:
        return Response({'detail': 'Document not found.'}, status=status.HTTP_404_NOT_FOUND)
    doc.file.delete(save=False)
    doc.delete()
    audit.log_action(request.user, 'kyc.document.deleted', 'Document', pk)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def document_download(request, pk):
    """Stream a stored document."""
    doc = Document.objects.filter(pk=pk).first()
    if doc is None:
        return Response({'detail': 'Document not found.'}, status=status.HTTP_404_NOT_FOUND)
    if doc.broker_id and doc.broker_id != get_broker(request).id and not request.user.is_staff:
        return Response({'detail': 'You do not have access to this document.'},
                        status=status.HTTP_403_FORBIDDEN)
    try:
        handle = doc.file.open('rb')
    except (FileNotFoundError, ValueError):
        return Response({'detail': 'File is missing from storage.'},
                        status=status.HTTP_404_NOT_FOUND)
    response = FileResponse(handle, content_type=doc.content_type or 'application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{doc.file.name.split("/")[-1]}"'
    return response


@api_view(['POST'])
def generate_price_list(request, pk):
    """Generate (and store) the price-list PDF for a project."""
    project = Project.objects.filter(pk=pk).first()
    if project is None:
        return Response({'detail': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)
    content, content_type = documents.build_price_list_pdf(project)
    doc = documents.save_document(
        kind=Document.PRICE_LIST,
        title=f'Price list - {project.name}',
        content=content,
        content_type=content_type,
    )
    audit.log_action(request.user, 'pricelist.generated', 'Document', doc.id, project=project.code)
    return Response(DocumentSerializer(doc, context={'request': request}).data,
                    status=status.HTTP_201_CREATED)


@api_view(['POST'])
def generate_demand_letter(request, pk):
    """Generate the demand letter for an approved booking."""
    booking = Booking.objects.select_related(
        'customer', 'plot', 'plot__project').filter(pk=pk).first()
    if booking is None:
        return Response({'detail': 'Booking not found.'}, status=status.HTTP_404_NOT_FOUND)
    if booking.status != Booking.STATUS_APPROVED:
        return Response({'detail': 'Demand letters are only generated for approved bookings.'},
                        status=status.HTTP_400_BAD_REQUEST)

    content, content_type = documents.build_demand_letter_pdf(booking)
    doc = documents.save_document(
        kind=Document.DEMAND_LETTER,
        title=f'Demand letter - {booking.plot.plot_number}',
        content=content,
        content_type=content_type,
        broker=booking.broker,
        booking=booking,
    )
    audit.log_action(request.user, 'demand_letter.generated', 'Document', doc.id,
                     booking=booking.id)
    return Response(DocumentSerializer(doc, context={'request': request}).data,
                    status=status.HTTP_201_CREATED)


@api_view(['GET'])
def kyc_summary(request):
    """Downloadable KYC summary for the signed-in broker."""
    broker = get_broker(request)
    content, content_type = documents.build_kyc_summary_pdf(broker)
    response = HttpResponse(content, content_type=content_type)
    response['Content-Disposition'] = 'attachment; filename="kyc-summary.pdf"'
    return response


# ---------------------------------------------------------------------------
# Administration
# ---------------------------------------------------------------------------

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_stats(request):
    return Response({
        'brokers': Broker.objects.count(),
        'kyc_pending': Broker.objects.filter(kyc_status=Broker.KYC_PENDING).count(),
        'kyc_approved': Broker.objects.filter(kyc_status=Broker.KYC_APPROVED).count(),
        'projects': Project.objects.count(),
        'plots': Plot.objects.count(),
        'available_plots': Plot.objects.filter(status=Plot.STATUS_AVAILABLE).count(),
        'on_hold_plots': Plot.objects.filter(status=Plot.STATUS_ON_HOLD).count(),
        'sold_plots': Plot.objects.filter(status=Plot.STATUS_SOLD).count(),
        'pending_bookings': Booking.objects.filter(status=Booking.STATUS_PENDING).count(),
        'approved_bookings': Booking.objects.filter(status=Booking.STATUS_APPROVED).count(),
        'rejected_bookings': Booking.objects.filter(status=Booking.STATUS_REJECTED).count(),
        'commissions': Commission.objects.count(),
        'unreleased_commissions': Commission.objects.filter(released=False).count(),
        'open_tickets': SupportTicket.objects.filter(status=SupportTicket.STATUS_OPEN).count(),
        'unread_notifications': Notification.objects.filter(read=False).count(),
    })


@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def admin_projects(request):
    """Create and list projects."""
    if request.method == 'GET':
        return Response(ProjectListSerializer(annotated_projects(), many=True).data)

    serializer = ProjectWriteSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    project = serializer.save()
    audit.log_action(request.user, 'project.created', 'Project', project.id, code=project.code)

    from .tasks import notify_new_project_task
    try:
        notify_new_project_task.delay(project.pk)
    except Exception:
        notifications.notify_brokers(
            Broker.objects.select_related('user').all(),
            title=f'New project launched: {project.name}',
            body=f'{project.location} — inventory now available.',
            kind=Notification.KIND_PROJECT,
            link=f'/projects/{project.pk}',
        )
    return Response(ProjectListSerializer(annotated_projects().filter(pk=project.pk).first()).data,
                    status=status.HTTP_201_CREATED)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAdminUser])
def admin_project_update(request, pk):
    project = Project.objects.filter(pk=pk).first()
    if project is None:
        return Response({'detail': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)
    serializer = ProjectWriteSerializer(project, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    audit.log_action(request.user, 'project.updated', 'Project', project.id)
    return Response(ProjectListSerializer(annotated_projects().filter(pk=project.pk).first()).data)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def admin_project_delete(request, pk):
    project = Project.objects.filter(pk=pk).first()
    if project is None:
        return Response({'detail': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)
    if project.bookings.exists():
        return Response({'detail': 'This project has bookings and cannot be deleted.'},
                        status=status.HTTP_400_BAD_REQUEST)
    audit.log_action(request.user, 'project.deleted', 'Project', project.id, code=project.code)
    project.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def admin_plots(request, pk):
    """List, create and bulk-create the plots of a project."""
    project = Project.objects.filter(pk=pk).first()
    if project is None:
        return Response({'detail': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(PlotWriteSerializer(project.plots.all(), many=True).data)

    payload = request.data
    if 'plots' in payload:
        serializer = BulkPlotSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        created = []
        with transaction.atomic():
            for plot_data in serializer.validated_data['plots']:
                plot_data['project'] = project
                created.append(Plot.objects.create(**plot_data))
        audit.log_action(request.user, 'plots.bulk_created', 'Project', project.id,
                         count=len(created))
        return Response(PlotWriteSerializer(created, many=True).data, status=status.HTTP_201_CREATED)

    serializer = PlotWriteSerializer(data={**payload, 'project': project.pk})
    serializer.is_valid(raise_exception=True)
    plot = serializer.save()
    audit.log_action(request.user, 'plot.created', 'Plot', plot.id, project=project.code)
    return Response(PlotWriteSerializer(plot).data, status=status.HTTP_201_CREATED)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAdminUser])
def admin_plot_update(request, pk):
    plot = Plot.objects.filter(pk=pk).first()
    if plot is None:
        return Response({'detail': 'Plot not found.'}, status=status.HTTP_404_NOT_FOUND)
    serializer = PlotWriteSerializer(plot, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    audit.log_action(request.user, 'plot.updated', 'Plot', plot.id)
    push_plot_update(plot, plot.status)
    return Response(PlotWriteSerializer(plot).data)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def admin_plot_delete(request, pk):
    plot = Plot.objects.filter(pk=pk).first()
    if plot is None:
        return Response({'detail': 'Plot not found.'}, status=status.HTTP_404_NOT_FOUND)
    if plot.bookings.exists():
        return Response({'detail': 'This plot has bookings and cannot be deleted.'},
                        status=status.HTTP_400_BAD_REQUEST)
    audit.log_action(request.user, 'plot.deleted', 'Plot', plot.id)
    plot.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_bookings(request):
    qs = Booking.objects.select_related(
        'plot', 'plot__project', 'customer', 'broker__user').all()
    status_filter = request.query_params.get('status')
    if status_filter:
        qs = qs.filter(status=status_filter)
    return Response(BookingSerializer(qs, many=True).data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_decide_booking(request, pk):
    booking = Booking.objects.select_related('plot', 'plot__project').filter(pk=pk).first()
    if booking is None:
        return Response({'detail': 'Booking not found.'}, status=status.HTTP_404_NOT_FOUND)
    if booking.status != Booking.STATUS_PENDING:
        return Response({'detail': 'This booking has already been decided.'},
                        status=status.HTTP_400_BAD_REQUEST)

    action = request.data.get('action')
    if action not in ('approve', 'reject'):
        return Response({'detail': 'Action must be "approve" or "reject".'},
                        status=status.HTTP_400_BAD_REQUEST)

    if action == 'approve':
        booking.status = Booking.STATUS_APPROVED
        booking.plot.status = Plot.STATUS_SOLD
        gross = booking.plot.total_cost * booking.commission_pct / Decimal(100)
        tds = gross * TDS_PCT / Decimal(100)
        Commission.objects.create(
            booking=booking,
            broker=booking.broker,
            amount=round(gross, 2),
            tds_pct=TDS_PCT,
            tds_amount=round(tds, 2),
            net_amount=round(gross - tds, 2),
        )
    else:
        booking.status = Booking.STATUS_REJECTED
        booking.plot.status = Plot.STATUS_AVAILABLE

    booking.decided_at = timezone.now()
    booking.save()
    booking.plot.save(update_fields=['status'])

    push_plot_update(booking.plot, booking.plot.status)
    audit.log_action(request.user, f'booking.{action}d', 'Booking', booking.id,
                     broker=booking.broker.user.email, plot=booking.plot.plot_number)

    if action == 'approve':
        notifications.notify(
            booking.broker,
            title=f'Booking approved — plot {booking.plot.plot_number}',
            body=(f'{booking.customer.name} · {booking.plot.project.name} · '
                  f'Commission {format(gross, ".2f")} (net {format(gross - tds, ".2f")}).'),
            kind=Notification.KIND_BOOKING,
            link='/bookings',
        )
        try:
            from .tasks import generate_demand_letter_task
            generate_demand_letter_task.delay(booking.id)
        except Exception:
            pass
    else:
        notifications.notify(
            booking.broker,
            title=f'Booking rejected — plot {booking.plot.plot_number}',
            body='The plot has been released back to available inventory.',
            kind=Notification.KIND_BOOKING,
            link='/bookings',
        )

    return Response(BookingSerializer(booking).data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_commissions(request):
    qs = Commission.objects.select_related(
        'booking__plot', 'booking__plot__project', 'booking__customer', 'broker__user')
    if request.query_params.get('released') == 'false':
        qs = qs.filter(released=False)
    return Response(CommissionSerializer(qs, many=True).data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_release_commission(request, pk):
    commission = Commission.objects.select_related('booking').filter(pk=pk).first()
    if commission is None:
        return Response({'detail': 'Commission not found.'}, status=status.HTTP_404_NOT_FOUND)
    if commission.released:
        return Response({'detail': 'Commission already released.'},
                        status=status.HTTP_400_BAD_REQUEST)

    commission.released = True
    commission.released_at = timezone.now()
    commission.save(update_fields=['released', 'released_at'])
    audit.log_action(request.user, 'commission.released', 'Commission', commission.id,
                     amount=str(commission.net_amount))
    notifications.notify(
        commission.broker,
        title='Commission released',
        body=f'{commission.net_amount} for {commission.booking.plot.plot_number} has been paid.',
        kind=Notification.KIND_COMMISSION,
        link='/commissions',
    )
    return Response(CommissionSerializer(commission).data)


@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def admin_tickets(request):
    if request.method == 'GET':
        qs = SupportTicket.objects.select_related('broker__user').all()
        status_filter = request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return Response(SupportTicketSerializer(qs, many=True).data)

    ticket = SupportTicket.objects.filter(pk=request.data.get('id')).first()
    if ticket is None:
        return Response({'detail': 'Ticket not found.'}, status=status.HTTP_404_NOT_FOUND)
    new_status = request.data.get('status')
    if new_status not in dict(SupportTicket.STATUS_CHOICES):
        return Response({'detail': 'Invalid status.'}, status=status.HTTP_400_BAD_REQUEST)
    ticket.status = new_status
    ticket.response = request.data.get('response', ticket.response)
    if new_status == SupportTicket.STATUS_RESOLVED:
        ticket.resolved_at = timezone.now()
    ticket.save()
    audit.log_action(request.user, 'ticket.updated', 'SupportTicket', ticket.id, status=new_status)
    notifications.notify(
        ticket.broker,
        title=f'Support ticket {new_status.replace("_", " ")}: {ticket.subject}',
        body=ticket.response or 'Your relationship manager has updated your ticket.',
        kind=Notification.KIND_SYSTEM,
        link='/support',
    )
    return Response(SupportTicketSerializer(ticket).data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_audit_log(request):
    qs = AuditLog.objects.all()[:200]
    return Response(AuditLogSerializer(qs, many=True).data)


@api_view(['GET', 'POST', 'PATCH'])
@permission_classes([IsAdminUser])
def admin_brokers(request):
    if request.method == 'GET':
        qs = Broker.objects.select_related('user').all()
        return Response(BrokerSerializer(qs, many=True).data)

    broker = Broker.objects.filter(pk=request.data.get('id')).first()
    if broker is None:
        return Response({'detail': 'Broker not found.'}, status=status.HTTP_404_NOT_FOUND)
    kyc_status = request.data.get('kyc_status')
    if kyc_status not in dict(Broker.KYC_CHOICES):
        return Response({'detail': 'Invalid KYC status.'}, status=status.HTTP_400_BAD_REQUEST)
    broker.kyc_status = kyc_status
    broker.save(update_fields=['kyc_status'])
    audit.log_action(request.user, 'broker.kyc_updated', 'Broker', broker.id, status=kyc_status)
    notifications.notify(
        broker,
        title=f'KYC {kyc_status}',
        body='Your KYC verification status has been updated.',
        kind=Notification.KIND_SYSTEM,
        link='/profile',
    )
    return Response(BrokerSerializer(broker).data)


@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def admin_broadcast(request):
    """Send a notification (new project / scheme) to every broker."""
    if request.method == 'GET':
        return Response({'brokers': Broker.objects.count()})

    title = request.data.get('title')
    if not title:
        return Response({'detail': 'A title is required.'}, status=status.HTTP_400_BAD_REQUEST)
    body = request.data.get('body', '')
    kind = request.data.get('kind', Notification.KIND_SCHEME)
    link = request.data.get('link', '')
    brokers = Broker.objects.select_related('user').all()
    notifications.notify_brokers(brokers, title=title, body=body, kind=kind, link=link)
    audit.log_action(request.user, 'notification.broadcast', 'Notification', 0,
                     title=title, recipients=brokers.count())
    return Response({'sent': brokers.count()}, status=status.HTTP_201_CREATED)
