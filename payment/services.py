import logging
from django.conf import settings
from django.utils.crypto import get_random_string
from sslcommerz_lib import SSLCOMMERZ
from .models import Payment

logger = logging.getLogger(__name__)

class PaymentService:
    """
    Handles payment transaction logic and interacts with SSLCommerz.
    Enforces consistency between payment records and booking states.
    """

    @staticmethod
    def get_ssl_client():
        """Initializes the SSLCommerz client with project settings."""
        ssl_settings = {
            'store_id': settings.SSL_STORE_ID,
            'store_pass': settings.SSL_STORE_PASS,
            'issandbox': settings.SSL_IS_SANDBOX
        }
        return SSLCOMMERZ(ssl_settings)

    
    @classmethod
    def initiate_payment_session(cls, user, booking, amount):
        """
        Creates a payment session with SSLCommerz and local Payment record.
        """
        if amount <= 0:
            logger.error(f"Cannot initiate payment for zero amount. Booking: {booking.booking_code}")
            return None

        sslcz = cls.get_ssl_client()
        
        # Calculate number of items (Table + Order Items)
        num_items = booking.order_items.count()
        if booking.seat:
            num_items += 1
        
        # Transaction ID is tied to the unique booking code with a random string to avoid duplicates
        # SSLCommerz Sandbox may reject identical tran_id if retry is attempted
        tran_id = f"tnx_{booking.booking_code}_{get_random_string(6).upper()}"
        backend_url = getattr(settings, 'BACKEND_URL', 'http://localhost:8000')

        # Mandatory Customer Info with fallbacks from Booking if User profile is empty
        cus_name = getattr(user, 'get_full_name', lambda: "")() or booking.name or "Valued Customer"
        cus_phone = str(getattr(user, 'phone', '') or booking.phone or '01700000000')
        cus_add1 = getattr(user, 'address', '') or booking.address or 'Dhaka, Bangladesh'
        cus_email = user.email or booking.email

        post_body = {
            'total_amount': amount,
            'currency': "BDT",
            'tran_id': tran_id,
            'success_url': f"{backend_url}/api/payment/success/",
            'fail_url': f"{backend_url}/api/payment/fail/",
            'cancel_url': f"{backend_url}/api/payment/cancel/",
            'emi_option': 0,
            'cus_name': cus_name,
            'cus_email': cus_email,
            'cus_phone': cus_phone,
            'cus_add1': cus_add1,
            'cus_city': "Dhaka",
            'cus_country': "Bangladesh",
            'shipping_method': "NO",
            'num_of_item': num_items,
            'product_name': "Restaurant Booking",
            'product_category': "General",
            'product_profile': "general",
        }

        logger.info(f"Initiating SSLCommerz session for {tran_id} with amount {amount}")
        response = sslcz.createSession(post_body)
        
        if response.get('status') == 'SUCCESS':
            # Upsert the payment record
            Payment.objects.update_or_create(
                booking=booking,
                defaults={
                    'transaction_id': tran_id,
                    'amount': amount,
                    'status': 'PENDING'
                }
            )
            return response.get('GatewayPageURL')
        
        logger.error(f"SSLCommerz session creation failed: {response}")
        return None

    @staticmethod
    def handle_payment_success(tran_id):
        """Updates payment and booking status on successful transaction."""
        try:
            payment = Payment.objects.get(transaction_id=tran_id)
            payment.status = 'SUCCESS'
            payment.save()

            booking = payment.booking
            booking.is_paid = True
            booking.status = 'CONFIRMED'
            booking.save()
            return True
        except Payment.DoesNotExist:
            logger.error(f"Success callback received for non-existent transaction: {tran_id}")
            return False

    @staticmethod
    def handle_payment_failure(tran_id, is_cancel=False):
        """Updates status to FAILED or CANCELLED."""
        try:
            payment = Payment.objects.get(transaction_id=tran_id)
            payment.status = 'FAILED'
            payment.save()
            return True
        except Payment.DoesNotExist:
            logger.error(f"Failure/Cancel callback received for non-existent transaction: {tran_id}")
            return False
