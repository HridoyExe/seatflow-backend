from .views import api_root_view
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('', api_root_view, name="api-root"),
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.jwt")),

    path("auth/", include("accounts.urls")),
    path("api/menu/", include("menu.urls")),
    path("api/booking/", include("booking.urls")),
    path("api/payment/", include("payment.urls")),
    
    # Swagger documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

urlpatterns+= static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)