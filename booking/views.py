from rest_framework.viewsets import ModelViewSet
from .models import Seat, Booking
from .serializers import SeatSerializer, BookingSerializer


class SeatViewSet(ModelViewSet):
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer


class BookingViewSet(ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer