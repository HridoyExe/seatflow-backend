from django.contrib import admin
from .models import Seat, Booking


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ("seat_number", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("seat_number",)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "booking_code",
        "user",
        "seat",
        "amount",
        "is_paid",
        "is_confirmed",
        "created_at",
    )

    list_filter = ("is_paid", "is_confirmed", "created_at")
    search_fields = ("booking_code", "phone", "email")