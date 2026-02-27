from django.urls import path, include


urlpatterns = [
    path("menu/", include("menu.urls")),
    path("booking/", include("booking.urls")),
    path("accounts/", include("accounts.urls")),
]