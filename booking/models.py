from django.db import models
from accounts.models import User
from menu.models import MenuItem
from django.utils import timezone


class Section(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Seat(models.Model):
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name="seats",
        null=True,
        blank=True
    )
    seat_number = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["seat_number"] 

    def __str__(self):
        return f"{self.seat_number} ({self.section.name if self.section else 'No Section'})"

class Booking(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bookings"
    )

    seat = models.ForeignKey(
        Seat,
        on_delete=models.CASCADE,
        related_name="seat_bookings"
    )

    booking_code = models.CharField(max_length=100, unique=True)

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()

    special_request = models.TextField(blank=True)

    booking_date = models.DateField(default=timezone.now)
    start_time = models.TimeField(default=timezone.now)
    end_time = models.TimeField(default=timezone.now)

    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    is_paid = models.BooleanField(default=False)
    is_confirmed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.booking_code
        
    def update_total_amount(self):
        # We can set a base seat price here if required, currently assuming 0 base cost or handled externally.
        total = sum(item.get_cost() for item in self.order_items.all())
        self.amount = total
        self.save(update_fields=['amount'])


class OrderItem(models.Model):
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="order_items"
    )
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE,
        related_name="order_items"
    )
    quantity = models.PositiveIntegerField(default=1)

    def get_cost(self):
        return self.menu_item.price * self.quantity

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.booking.update_total_amount()

    def delete(self, *args, **kwargs):
        booking = self.booking
        super().delete(*args, **kwargs)
        booking.update_total_amount()

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name} (Booking: {self.booking.booking_code})"
