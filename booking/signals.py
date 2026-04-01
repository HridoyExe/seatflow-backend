from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import OrderItem
from .services import BookingService

@receiver(post_save, sender=OrderItem)
@receiver(post_delete, sender=OrderItem)
def update_booking_amount_on_order_item_change(sender, instance, **kwargs):
    """
    Automatically recalculate the booking total whenever 
    items are added or removed.
    """
    BookingService.update_booking_total(instance.booking)
