from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SeatViewSet, BookingViewSet, OrderItemViewSet, DashboardStatsAPIView

router = DefaultRouter()
router.register(r"seats", SeatViewSet, basename="seat")
router.register(r"bookings", BookingViewSet)
router.register(r"order-items", OrderItemViewSet, basename="orderitem")  

urlpatterns = [
    path("stats/", DashboardStatsAPIView.as_view(), name="dashboard-stats"),
    path("", include(router.urls)),
]