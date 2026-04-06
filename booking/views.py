from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from django.db import transaction
from django.db.models import Sum
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
    list=extend_schema(description="List all bookings. Admins see all, Members see only their own."),
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

        # Admin sees everything, Member sees only their own
        if self.request.user.role == 'ADMIN':
            return Booking.objects.select_related(
                "user", 
                "seat", 
                "seat__section"
            ).prefetch_related(
                "order_items", 
                "order_items__menu_item"
            ).all()

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
        # Delegate creation logic to Service layer
        booking = BookingService.create_booking(
            user=self.request.user,
            data=serializer.validated_data
        )
        # Crucial: Save the instance into the serializer so DRF returns the created object data (including ID)
        serializer.instance = booking

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.is_paid:
            raise serializers.ValidationError("You Cannot Update a Paid Booking")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.is_paid:
            raise serializers.ValidationError("You cannot cancel a paid booking")
        instance.delete()

class DashboardStatsAPIView(APIView):
    permission_classes = [IsAuthenticatedUser]

    @extend_schema(
        description="Fetch statistics for the authenticated user based on their role.",
        responses={200: OpenApiTypes.OBJECT}
    )
    def get(self, request):
        user = request.user
        
        if user.role == 'ADMIN':
            stats = {
                "total_revenue": Booking.objects.aggregate(Sum('amount'))['amount__sum'] or 0,
                "total_bookings": Booking.objects.filter(seat__isnull=False).count(),
                "total_orders": Booking.objects.filter(seat__isnull=True).count(),
                "active_seats": Seat.objects.filter(is_active=True).count(),
                "recent_transactions": Booking.objects.order_by('-id')[:5].values('id', 'booking_code', 'name', 'amount', 'is_paid', 'booking_date', 'start_time')
            }
        else:
            stats = {
                "total_visits": Booking.objects.filter(user=user, is_paid=True).count(),
                "loyalty_points": int((Booking.objects.filter(user=user, is_paid=True).aggregate(Sum('amount'))['amount__sum'] or 0) * 0.1),
                "upcoming_bookings": Booking.objects.filter(user=user, booking_date__gte=date.today(), seat__isnull=False).count(),
                "upcoming_orders": Booking.objects.filter(user=user, booking_date__gte=date.today(), seat__isnull=True).count(),
                "total_bookings": Booking.objects.filter(user=user, seat__isnull=False).count(),
                "total_orders": Booking.objects.filter(user=user, seat__isnull=True).count(),
            }
        
        return Response(stats)

@extend_schema_view(
    retrieve=extend_schema(description="Get order item details"),
    create=extend_schema(description="Add a new item to an existing booking. Can only add to own bookings."),
)
class OrderItemViewSet(ModelViewSet):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticatedUser]

    @extend_schema(
        description="List all order items. Admins see all, Members see only their own.",
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

        if self.request.user.role == 'ADMIN':
             queryset = OrderItem.objects.select_related("booking","menu_item").all()
        else:
             queryset = OrderItem.objects.select_related("booking","menu_item").filter(booking__user=self.request.user)

        booking_id = self.request.query_params.get("booking")
        if booking_id:
            queryset = queryset.filter(booking_id=booking_id)

        return queryset

    def perform_create(self, serializer):
        booking = serializer.validated_data.get("booking")
        if booking and booking.user != self.request.user:
            raise serializers.ValidationError("You cannot add items to others booking")

        serializer.save(booking=booking)

    def update(self, request, *args, **kwargs):
        raise serializers.ValidationError("Update is not allowed for Order Items")

    def partial_update(self, request, *args, **kwargs):
        raise serializers.ValidationError("Update is not allowed for Order Items")

    def perform_destroy(self, instance):
        if instance.booking.is_paid:
            raise serializers.ValidationError("You cannot cancel an order item for a paid booking")
        instance.delete()