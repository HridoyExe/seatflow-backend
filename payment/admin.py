from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "booking",
        "transaction_id",
        "amount",
        "status",
        "created_at",
    )

    list_filter = ("status",)
    search_fields = ("transaction_id",)