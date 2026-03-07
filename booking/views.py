from rest_framework.viewsets import ModelViewSet
from rest_framework import serializers
from django.db import transaction
from .permissions import IsAuthenticatedUser, IsOwner, IsAdminOrReadOnly
from .models import Section, Seat, Booking, OrderItem
from .serializers import (
    SectionSerializer,
    SeatSerializer,
    BookingSerializer,
    OrderItemSerializer,
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.decorators import method_decorator

@method_decorator(name='list', decorator=swagger_auto_schema(operation_description="List all sections"))
@method_decorator(name='create', decorator=swagger_auto_schema(operation_description="Create a new section (Admin only)"))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(operation_description="Get section details"))
@method_decorator(name='update', decorator=swagger_auto_schema(operation_description="Update a section (Admin only)"))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(operation_description="Partially update a section (Admin only)"))
@method_decorator(name='destroy', decorator=swagger_auto_schema(operation_description="Delete a section (Admin only)"))
class SectionViewSet(ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Section.objects.all()
    serializer_class = SectionSerializer


@method_decorator(name='list', decorator=swagger_auto_schema(operation_description="List all seats"))
@method_decorator(name='create', decorator=swagger_auto_schema(operation_description="Create a new seat (Admin only)"))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(operation_description="Get seat details"))
@method_decorator(name='update', decorator=swagger_auto_schema(operation_description="Update a seat (Admin only)"))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(operation_description="Partially update a seat (Admin only)"))
@method_decorator(name='destroy', decorator=swagger_auto_schema(operation_description="Delete a seat (Admin only)"))
class SeatViewSet(ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer

    def perform_update(self, serializer):
        instance = self.get_object()

        if instance.seat_bookings.exists():
            raise serializers.ValidationError(
                "This seat has active bookings, cannot update."
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

@method_decorator(name='list', decorator=swagger_auto_schema(operation_description="List all bookings for the currently authenticated user"))
@method_decorator(name='create', decorator=swagger_auto_schema(operation_description="Create a new booking. Maximum 4 paid bookings per user."))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(operation_description="Get booking details"))
@method_decorator(name='update', decorator=swagger_auto_schema(operation_description="Update a booking. Cannot update if already paid."))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(operation_description="Partially update a booking. Cannot update if already paid."))
@method_decorator(name='destroy', decorator=swagger_auto_schema(operation_description="Cancel/Delete a booking"))
class BookingViewSet(ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticatedUser]
    queryset = Booking.objects.all()

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Booking.objects.none()

        return Booking.objects.select_related(
            "user",
            "seat"
        ).filter(user=self.request.user)

    @transaction.atomic
    def perform_create(self, serializer):
        seat = serializer.validated_data.get("seat")

        if not seat.is_active:
            raise serializers.ValidationError("This seat is not active")

        if Booking.objects.filter(seat=seat, is_paid=True).exists():
            raise serializers.ValidationError("This seat is already booked")

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

    def perform_destroy(self, instance):
        if instance.is_paid:
            raise serializers.ValidationError(
                "You cannot cancel a paid booking"
            )
        instance.delete()

@method_decorator(name='retrieve', decorator=swagger_auto_schema(operation_description="Get order item details"))
@method_decorator(name='create', decorator=swagger_auto_schema(operation_description="Add a new item to an existing booking. Can only add to own bookings."))
class OrderItemViewSet(ModelViewSet):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticatedUser]

    @swagger_auto_schema(
        operation_description="List all order items for the currently authenticated user",
        manual_parameters=[
            openapi.Parameter(
                'booking', 
                openapi.IN_QUERY, 
                description="Filter items by a specific booking ID", 
                type=openapi.TYPE_INTEGER
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return OrderItem.objects.none()

        queryset = OrderItem.objects.select_related(
            "booking",
            "menu_item"
        ).filter(booking__user=self.request.user)

        booking_id = self.request.query_params.get("booking")
        if booking_id:
            queryset = queryset.filter(booking_id=booking_id)

        return queryset

    def perform_create(self, serializer):
        booking = serializer.validated_data.get("booking")
        if booking.user != self.request.user:
            raise serializers.ValidationError(
                "You cannot add items to others booking"
            )

        serializer.save(booking=booking)

    def update(self, request, *args, **kwargs):
        raise serializers.ValidationError("Update is not allowed for Order Items")

    def partial_update(self, request, *args, **kwargs):
        raise serializers.ValidationError("Update is not allowed for Order Items")

    def perform_destroy(self, instance):
        if instance.booking.is_paid:
            raise serializers.ValidationError(
                "You cannot cancel an order item for a paid booking"
            )
        instance.delete()