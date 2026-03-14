from django.urls import path
from .views import initiate_payment, payment_success, payment_fail, payment_cancel

urlpatterns = [
    path("initiate/", initiate_payment, name="initiate-payment"),
    path("success/", payment_success, name="payment-success"),
    path("fail/", payment_fail, name="payment-fail"),
    path("cancel/", payment_cancel, name="payment-cancel"),
]
