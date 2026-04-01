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
from .services import BookingService
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes
from django.utils.decorators import method_decorator

@extend_schema_view(
    list=extend_schema(description="List all sections"),
    create=extend_schema(description="Create a new section (Admin only)"),
    retrieve=extend_schema(description="Get section details"),
    update=extend_schema(description="Update a section (Admin only)"),
    partial_update=extend_schema(description="Partially update a section (Admin only)"),
    destroy=extend_schema(description="Delete a section (Admin only)"),
)
class SectionViewSet(ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Section.objects.all()
    serializer_class = SectionSerializer


@extend_schema_view(
    list=extend_schema(description="List all seats"),
    create=extend_schema(description="Create a new seat (Admin only)"),
    retrieve=extend_schema(description="Get seat details"),
    update=extend_schema(description="Update a seat (Admin only)"),
    partial_update=extend_schema(description="Partially update a seat (Admin only)"),
    destroy=extend_schema(description="Delete a seat (Admin only)"),
)
class SeatViewSet(ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Seat.objects.select_related("section").all()
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

@extend_schema_view(
    list=extend_schema(description="List all bookings for the currently authenticated user"),
    create=extend_schema(description="Create a new booking. Maximum 4 paid bookings per user."),
    retrieve=extend_schema(description="Get booking details"),
    update=extend_schema(description="Update a booking. Cannot update if already paid."),
    partial_update=extend_schema(description="Partially update a booking. Cannot update if already paid."),
    destroy=extend_schema(description="Cancel/Delete a booking"),
)
class BookingViewSet(ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticatedUser]
    queryset = Booking.objects.all()

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Booking.objects.none()

        return Booking.objects.select_related(
            "user", 
            "seat", 
            "seat__section"
        ).prefetch_related(
            "order_items", 
            "order_items__menu_item"
        ).filter(user=self.request.user)

    @transaction.atomic
    def perform_create(self, serializer):
        # Professional practice: business logic belongs in the service layer
        BookingService.create_booking(
            user=self.request.user,
            data=serializer.validated_data
        )

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

@extend_schema_view(
    retrieve=extend_schema(description="Get order item details"),
    create=extend_schema(description="Add a new item to an existing booking. Can only add to own bookings."),
)
class OrderItemViewSet(ModelViewSet):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticatedUser]

    @extend_schema(
        description="List all order items for the currently authenticated user",
        parameters=[
            OpenApiParameter(
                name='booking', 
                location=OpenApiParameter.QUERY, 
                description="Filter items by a specific booking ID", 
                type=OpenApiTypes.INT
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