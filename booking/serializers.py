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
            "is_active",
            "created_at",
        ]

class BookingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Booking
        fields = [
            "id",
            "user",
            "seat",
            "booking_code",
            "name",
            "phone",
            "email",
            "special_request",
            "amount",
            "is_paid",
            "is_confirmed",
            "created_at",
        ]

        extra_kwargs = {
            "booking_code": {"read_only": True},
            "user": {"read_only": True},
            "is_paid": {"read_only": True},
            "is_confirmed": {"read_only": True},
            "created_at": {"read_only": True},
        }

    def create(self, validated_data):
        validated_data["booking_code"] = "BOOK-" + get_random_string(6).upper()
        return super().create(validated_data)
class OrderItemSerializer(serializers.ModelSerializer):

    menu_item_name = serializers.CharField(
        source="menu_item.name",
        read_only=True
    )

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "booking",
            "menu_item",
            "menu_item_name",
            "quantity",
        ]

        extra_kwargs = {
            "booking": {"read_only": True},
        }