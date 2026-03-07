from rest_framework.viewsets import ModelViewSet
from rest_framework import serializers
from django.db import transaction

from .models import Section, Seat, Booking, OrderItem
from .serializers import (
    SectionSerializer,
    SeatSerializer,
    BookingSerializer,
    OrderItemSerializer,
)

class SectionViewSet(ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer

class SeatViewSet(ModelViewSet):
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer

    def perform_update(self, serializer):
        instance = self.get_object()
        new_seat_number = serializer.validated_data.get("seat_number")

        if instance.seat_bookings.exists():
            raise serializers.ValidationError(
                "This seat has active bookings, cannot update."
            )

        if new_seat_number:
            if Seat.objects.filter(seat_number=new_seat_number)\
                    .exclude(id=instance.id).exists():
                raise serializers.ValidationError(
                    "Seat number already exists."
                )

        serializer.save()

    def perform_destroy(self, instance):

        if instance.seat_bookings.filter(is_paid=True).exists():
            raise serializers.ValidationError(
                "Cannot delete a seat with paid bookings."
            )

        if instance.seat_bookings.exists():
            raise serializers.ValidationError(
                "This seat has active bookings, cannot delete."
            )

        instance.delete()

class BookingViewSet(ModelViewSet):
    serializer_class = BookingSerializer
    queryset = Booking.objects.all()

    def get_queryset(self):
        return Booking.objects.select_related(
            "user",
            "seat"
        ).filter(
            user=self.request.user
        )

    @transaction.atomic
    def perform_create(self, serializer):
        seat = serializer.validated_data.get("seat")

        if not seat.is_active:
            raise serializers.ValidationError(
                "This seat is not active"
            )

        if Booking.objects.filter(seat=seat, is_paid=True).exists():
            raise serializers.ValidationError(
                "This seat is already booked"
            )

        user_paid_count = Booking.objects.filter(
            user=self.request.user,
            is_paid=True
        ).count()

        if user_paid_count >= 4:
            raise serializers.ValidationError(
                "You cannot book more than 4 paid seats"
            )

        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        instance = self.get_object()

        if instance.is_paid:
            raise serializers.ValidationError(
                "You Cannot Update a Paid Booking"
            )

        serializer.save()

class OrderItemViewSet(ModelViewSet):
    queryset = OrderItem.objects.select_related(
        "booking",
        "menu_item"
    ).all()

    serializer_class = OrderItemSerializer

    def perform_create(self, serializer):
        booking = serializer.validated_data.get("booking")
        serializer.save(booking=booking)

    def update(self, request, *args, **kwargs):
        raise serializers.ValidationError(
            "Update is not allowed for Order Items"
        )
    def partial_update(self, request, *args, **kwargs):
        raise serializers.ValidationError(
            "Update is not allowed for Order Items"
        )
    def destroy(self, request, *args, **kwargs):
        raise serializers.ValidationError(
            "Delete is not allowed for Order Items"
        )