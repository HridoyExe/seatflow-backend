from rest_framework import serializers
from django.utils.crypto import get_random_string
from .models import Section, Seat, Booking, OrderItem

class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = [
            "id",
            "name",
            "description",
        ]

class SeatSerializer(serializers.ModelSerializer):

    class Meta:
        model = Seat
        fields = [
            "id",
            "section",
            "seat_number",
            "capacity",
            "is_active",
            "created_at",
        ]

class OrderItemSerializer(serializers.ModelSerializer):

    menu_item_name = serializers.CharField(
        source="menu_item.name",
        read_only=True
    )
    
    # Including price for receipt and display
    price = serializers.DecimalField(
        source="menu_item.price", 
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "booking",
            "menu_item",
            "menu_item_name",
            "price",
            "quantity",
        ]

    def to_internal_value(self, data):
        # We need a mutable copy for QueryDicts
        if hasattr(data, 'copy'):
            data = data.copy()
        return super().to_internal_value(data)

        extra_kwargs = {
            "booking": {"required": False},
        }

class BookingSerializer(serializers.ModelSerializer):

    seat_number = serializers.CharField(source="seat.seat_number", read_only=True)
    section_name = serializers.CharField(source="seat.section.name", read_only=True)
    order_items = OrderItemSerializer(many=True, read_only=True)
    
    def to_internal_value(self, data):
        # Mutualize data for compatibility
        if hasattr(data, 'copy'):
            data = data.copy()
        return super().to_internal_value(data)

    class Meta:
        model = Booking
        fields = [
            "id",
            "user",
            "seat",
            "seat_number",
            "section_name",
            "booking_code",
            "name",
            "phone",
            "email",
            "address",
            "special_request",
            "booking_date",
            "start_time",
            "end_time",
            "amount",
            "status",
            "is_paid",
            "is_confirmed",
            "order_items",
            "created_at",
        ]

        extra_kwargs = {
            "booking_code": {"read_only": True},
            "user": {"read_only": True},
            "amount": {"read_only": True},
            "status": {"read_only": True},
            "is_paid": {"read_only": True},
            "is_confirmed": {"read_only": True},
            "created_at": {"read_only": True},
        }

    def validate(self, attrs):
        booking_date = attrs.get('booking_date')
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')

        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError({"end_time": "End time must be after start time."})

        # Example validation for future dates, skipped for simplicity if we allow same day.
        # However, ensuring date is not empty if required can be done here.
        
        return attrs

    def create(self, validated_data):
        validated_data["booking_code"] = "BOOK-" + get_random_string(6).upper()
        return super().create(validated_data)