from django.db import transaction
from django.utils.crypto import get_random_string
from .models import Booking, Seat
from .exceptions import SeatUnavailableError, BookingLimitExceededError, InactiveSeatError
from django.db.models import Q

class BookingService:
    """
    Handles core booking operations and business rules.
    Decoupled from models and views for maintainability.
    """

    @staticmethod
    def validate_seat_availability(seat, booking_date, start_time, end_time):
        # 1. Simple status check
        if not seat.is_active:
            raise InactiveSeatError()

        # 2. Check for overlapping time slots
        # Rule: A booking overlaps if (new_start < exist_end) AND (new_end > exist_start)
        overlap = Booking.objects.filter(
            seat=seat,
            booking_date=booking_date,
            is_paid=True
        ).filter(
            Q(start_time__lt=end_time, end_time__gt=start_time)
        ).exists()

        if overlap:
            raise SeatUnavailableError()

    @staticmethod
    def check_user_booking_limit(user):
        """Limit each user to 4 active/paid bookings concurrently."""
        active_count = Booking.objects.filter(user=user, is_paid=True).count()
        if active_count >= 4:
            raise BookingLimitExceededError()

    @classmethod
    @transaction.atomic
    def create_booking(cls, user, data):
        seat = data.get('seat')
        
        if seat:
            cls.validate_seat_availability(
                seat, 
                data.get('booking_date'), 
                data.get('start_time'), 
                data.get('end_time')
            )
        cls.check_user_booking_limit(user)

        # Generate unique booking code
        booking_code = f"SF-{get_random_string(8).upper()}"
        
        booking = Booking.objects.create(
            user=user,
            booking_code=booking_code,
            **data
        )
        cls.update_booking_total(booking)
        return booking

    @staticmethod
    def update_booking_total(booking):
        """Recalculates the total amount based on associated order items and seat fee."""
        # Baseline fee for table reservation (৳15.00)
        base_fee = 15.00 if booking.seat else 0.00
        
        items_total = sum(item.get_cost() for item in booking.order_items.all())
        total = float(base_fee) + float(items_total)
        
        # Ensure minimum amount for payment gateway (SSLCommerz needs > 0)
        # If the total is > 0 but < 10, we can force it to 10 or just leave it.
        # However, 0 must be avoided.
        booking.amount = round(total, 2)
        booking.save(update_fields=['amount'])
