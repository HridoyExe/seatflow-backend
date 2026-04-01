from django.test import TestCase
from django.utils import timezone
from .models import Section, Seat, Booking
from .services import BookingService
from .exceptions import SeatUnavailableError, BookingLimitExceededError
from accounts.models import User
import datetime

class BookingServiceTests(TestCase):
    """
    Unit tests for the BookingService layer.
    Industry-standard testing covers business rules and error cases.
    """

    def setUp(self):
        # Create common test data
        self.user = User.objects.create_user(
            email="tester@example.com", 
            password="testpassword123"
        )
        self.section = Section.objects.create(name="VIP Lounge")
        self.seat = Seat.objects.create(
            seat_number="V1", 
            capacity=2, 
            section=self.section,
            is_active=True
        )

    def test_seat_overlap_prevention(self):
        """Ensures that the service prevents double-booking a seat at the same time."""
        # 1. Create an initial confirmed booking
        Booking.objects.create(
            user=self.user,
            seat=self.seat,
            booking_code="EXISTING",
            booking_date=datetime.date.today(),
            start_time=datetime.time(10, 0),
            end_time=datetime.time(12, 0),
            is_paid=True, # Confirmed/Paid bookings should block others
            status='CONFIRMED'
        )

        # 2. Try to create another booking overlapping with the first one
        with self.assertRaises(SeatUnavailableError):
            BookingService.validate_seat_availability(
                seat=self.seat,
                booking_date=datetime.date.today(),
                start_time=datetime.time(11, 0), # Overlaps
                end_time=datetime.time(13, 0)
            )

    def test_user_booking_limit(self):
        """Ensures a user cannot exceed the maximum allowed paid bookings (4)."""
        # Create 4 confirmed bookings for the user
        for i in range(4):
            Booking.objects.create(
                user=self.user,
                seat=self.seat,
                booking_code=f"BOOK-{i}",
                is_paid=True
            )

        # Attempting to check limit should raise error
        with self.assertRaises(BookingLimitExceededError):
            BookingService.check_user_booking_limit(self.user)

    def test_create_booking_generates_code(self):
        """Ensures BookingService successfully creates a record with a unique code."""
        booking_data = {
            'seat': self.seat,
            'name': 'Test User',
            'phone': '01234567890',
            'email': 'test@example.com',
            'booking_date': datetime.date.today(),
            'start_time': datetime.time(14, 0),
            'end_time': datetime.time(16, 0)
        }

        booking = BookingService.create_booking(self.user, booking_data)
        
        self.assertIsInstance(booking, Booking)
        self.assertTrue(booking.booking_code.startswith("SF-"))
        self.assertEqual(booking.status, "PENDING")
