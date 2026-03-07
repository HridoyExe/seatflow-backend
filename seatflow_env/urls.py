from .views import api_root_view
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
schema_view = get_schema_view(
   openapi.Info(
      title="SeatFlow",
      default_version='v1',
      description="API documentation for SeatFlow project",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@seatflow.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)
urlpatterns = [
    path('',api_root_view, name="api-root"),
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.jwt")),

    path("auth/", include("accounts.urls")),
    path("api/menu/", include("menu.urls")),
    path("api/booking/", include("booking.urls")),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

urlpatterns+= static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)