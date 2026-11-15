"""API views for the InventoryOne Broker Web App."""
from decimal import Decimal

from django.contrib.auth.models import User
from django.conf import settings
from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from .models import Booking, Broker, Commission, Customer, OTPCode, Plot, Project
from .serializers import (
    BookingSerializer,
    BrokerSerializer,
    CommissionSerializer,
    CustomerSerializer,
    ProjectDetailSerializer,
    ProjectListSerializer,
)

TDS_PCT = Decimal(10)


def get_broker(request):
    """Return the Broker profile of the authenticated user."""
    return Broker.objects.select_related('user').get(user=request.user)


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
        # Mail delivery is stubbed in development; surface the code in the response.
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
    })


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
    return Response(CommissionSerializer(commission).data)
