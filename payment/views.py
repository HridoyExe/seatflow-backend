from django.shortcuts import redirect
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, inline_serializer
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers
from sslcommerz_lib import SSLCOMMERZ
from .models import Payment
from booking.models import Booking

@extend_schema(
    request=inline_serializer(
        name='InitiatePaymentRequest',
        fields={
            'amount': serializers.FloatField(required=False),
            'orderId': serializers.IntegerField(),
            'numItems': serializers.IntegerField(default=1),
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
    print(request.data)
    user = request.user
    amount = request.data.get("amount")
    order_id = request.data.get("orderId") # This corresponds to Booking ID
    num_items = request.data.get("numItems", 1)
    
    # Try to find the booking
    try:
        booking = Booking.objects.get(id=order_id, user=user)
    except Booking.DoesNotExist:
        return Response({"error": "Booking not found"}, status=404)

    # Use actual amount from booking if not provided or to ensure correctness
    if not amount:
        amount = float(booking.amount)

    settings_ssl = { 
        'store_id': settings.SSL_STORE_ID, 
        'store_pass': settings.SSL_STORE_PASS, 
        'issandbox': settings.SSL_IS_SANDBOX
    }
    sslcz = SSLCOMMERZ(settings_ssl)
    
    post_body = {}
    post_body['total_amount'] = amount
    post_body['currency'] = "BDT"
    post_body['tran_id'] = f"tnx_{booking.booking_code}" # Using booking code for transaction ID
    
    # Using BACKEND_URL from settings
    backend_url = getattr(settings, 'BACKEND_URL', 'http://localhost:8000')
    post_body['success_url'] = f"{backend_url}/api/payment/success/"
    post_body['fail_url'] = f"{backend_url}/api/payment/fail/"
    post_body['cancel_url'] = f"{backend_url}/api/payment/cancel/"
    
    post_body['emi_option'] = 0
    post_body['cus_name'] = f"{user.first_name} {user.last_name}"
    post_body['cus_email'] = user.email
    # Handling potential differing field names in User model
    post_body['cus_phone'] = str(user.phone) if hasattr(user, 'phone') else ""
    post_body['cus_add1'] = getattr(user, 'address', 'Dhaka')
    post_body['cus_city'] = "Dhaka"
    post_body['cus_country'] = "Bangladesh"
    post_body['shipping_method'] = "NO"
    post_body['multi_card_name'] = ""
    post_body['num_of_item'] = num_items
    post_body['product_name'] = "Restaurant Booking"
    post_body['product_category'] = "General"
    post_body['product_profile'] = "general"

    response = sslcz.createSession(post_body)
    
    if response.get('status') == 'SUCCESS':
        # Create or update payment record
        Payment.objects.update_or_create(
            booking=booking,
            defaults={
                'transaction_id': post_body['tran_id'],
                'amount': amount,
                'status': 'PENDING'
            }
        )
        return Response({
            "payment_url": response['GatewayPageURL']
        })
    else:
        return Response({
            "error": response
        }, status=400)

@extend_schema(
    request=inline_serializer(
        name='PaymentCallbackRequest',
        fields={'tran_id': serializers.CharField()}
    ),
    responses={302: None, 404: OpenApiTypes.OBJECT}
)
@csrf_exempt
@api_view(['POST'])
def payment_success(request):
    data = request.data
    tran_id = data.get('tran_id')
    # Update payment status
    try:
        payment = Payment.objects.get(transaction_id=tran_id)
        payment.status = 'SUCCESS'
        payment.save()
        
        # Also update booking status
        booking = payment.booking
        booking.is_paid = True
        booking.save()
        
        # Redirect to frontend success page
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
        return redirect(f"{frontend_url}/payment/success?tran_id={tran_id}")
    except Payment.DoesNotExist:
        return Response({"error": "Payment record not found"}, status=404)

@extend_schema(
    request=inline_serializer(
        name='PaymentCallbackRequestFail', # Changed name to avoid duplicate in schema if needed, but spectacular might handle it.
        fields={'tran_id': serializers.CharField()}
    ),
    responses={302: None, 404: OpenApiTypes.OBJECT}
)
@csrf_exempt
@api_view(['POST'])
def payment_fail(request):
    data = request.data
    tran_id = data.get('tran_id')
    try:
        payment = Payment.objects.get(transaction_id=tran_id)
        payment.status = 'FAILED'
        payment.save()
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
        return redirect(f"{frontend_url}/payment/fail?tran_id={tran_id}")
    except Payment.DoesNotExist:
        return Response({"error": "Payment record not found"}, status=404)

@extend_schema(
    request=inline_serializer(
        name='PaymentCallbackRequestCancel',
        fields={'tran_id': serializers.CharField()}
    ),
    responses={302: None, 404: OpenApiTypes.OBJECT}
)
@csrf_exempt
@api_view(['POST'])
def payment_cancel(request):
    data = request.data
    tran_id = data.get('tran_id')
    try:
        payment = Payment.objects.get(transaction_id=tran_id)
        payment.status = 'FAILED' # Or define a CANCELLED status
        payment.save()
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
        return redirect(f"{frontend_url}/payment/cancel?tran_id={tran_id}")
    except Payment.DoesNotExist:
        return Response({"error": "Payment record not found"}, status=404)
