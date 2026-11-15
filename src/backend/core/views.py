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

from .models import (
    Broker,
    OTPCode,
)
from .serializers import BrokerSerializer

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


