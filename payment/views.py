from django.shortcuts import redirect
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, inline_serializer
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers
from sslcommerz_lib import SSLCOMMERZ
from .models import Payment
from booking.models import Booking

from .services import PaymentService

@extend_schema(
    request=inline_serializer(
        name='InitiatePaymentRequest',
        fields={
            'amount': serializers.FloatField(required=True),
            'orderId': serializers.IntegerField(),
        }
    ),
    responses={
        200: inline_serializer(
            name='InitiatePaymentResponse',
            fields={'payment_url': serializers.URLField()}
        ),
        400: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT,
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_payment(request):
    user = request.user
    order_id = request.data.get("orderId")
    try:
        booking = Booking.objects.get(id=order_id, user=user)
    except Booking.DoesNotExist:
        return Response({"error": "Booking not found"}, status=404)

    # Professional systems rely on internal calculations to avoid price tampering.
    # We call update_booking_total as a failsafe to ensure the food items are included.
    from booking.services import BookingService
    BookingService.update_booking_total(booking)
    
    amount = float(booking.amount)
    payment_url = PaymentService.initiate_payment_session(user, booking, amount)
    
    if payment_url:
        return Response({"payment_url": payment_url})
    
    return Response(
        {"error": "Failed to create SSLCommerz payment session. Check logs for details."}, 
        status=400
    )

@extend_schema(
    description="Callback for successful payments from SSLCommerz. Notifies the system to update booking status.",
    request=inline_serializer(
        name='PaymentSuccessRequest',
        fields={'tran_id': serializers.CharField()}
    ),
    responses={200: OpenApiTypes.OBJECT}
)
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def payment_success(request):
    # SSLCommerz sends data as form-data in a POST redirect. 
    # DRF's request.data handles both JSON and Form-Data.
    tran_id = request.data.get('tran_id') or request.POST.get('tran_id')
    
    if not tran_id:
        logger.error(f"Success callback received without transaction ID. Data: {request.data}")
        return Response({"error": "Transaction ID missing"}, status=400)

    if PaymentService.handle_payment_success(tran_id):
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
        return redirect(f"{frontend_url}/payment/success?tran_id={tran_id}")
    
    return Response({"error": "Payment validation failed or transaction not found"}, status=400)

@extend_schema(
    description="Callback for failed payments from SSLCommerz. Updates booking to FAILED status.",
    request=inline_serializer(
        name='PaymentFailRequest',
        fields={'tran_id': serializers.CharField()}
    ),
    responses={200: OpenApiTypes.OBJECT}
)
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def payment_fail(request):
    tran_id = request.data.get('tran_id') or request.POST.get('tran_id')
    PaymentService.handle_payment_failure(tran_id)
    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
    return redirect(f"{frontend_url}/payment/fail?tran_id={tran_id}")

@extend_schema(
    description="Callback for cancelled payments from SSLCommerz. Updates booking to CANCELLED status.",
    request=inline_serializer(
        name='PaymentCancelRequest',
        fields={'tran_id': serializers.CharField()}
    ),
    responses={200: OpenApiTypes.OBJECT}
)
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def payment_cancel(request):
    tran_id = request.data.get('tran_id') or request.POST.get('tran_id')
    PaymentService.handle_payment_failure(tran_id, is_cancel=True)
    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
    return redirect(f"{frontend_url}/payment/cancel?tran_id={tran_id}")
