from .views import api_root_view
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('',api_root_view, name="api-root"),
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.jwt")),

     path("auth/", include("accounts.urls")),
    path("api/menu/", include("menu.urls")),
    path("api/booking/", include("booking.urls")),
]