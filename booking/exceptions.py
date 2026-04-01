from rest_framework.exceptions import ValidationError
from rest_framework import status

class BookingError(ValidationError):
    """Base exception for booking-related errors."""
    status_code = status.HTTP_400_BAD_REQUEST

class SeatUnavailableError(BookingError):
    default_detail = "This seat is already booked for the selected time slot."
    default_code = "seat_unavailable"

class BookingLimitExceededError(BookingError):
    default_detail = "You have reached the maximum limit of active bookings."
    default_code = "booking_limit_exceeded"

class InactiveSeatError(BookingError):
    default_detail = "This seat is currently inactive and cannot be booked."
    default_code = "inactive_seat"
