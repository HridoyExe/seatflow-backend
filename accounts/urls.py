from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, SendOTpView, VerifyOtpView, LoginView,RegisterView


router = DefaultRouter()
router.register(r"users", UserViewSet)


urlpatterns = [
    path("register/",RegisterView.as_view()),
    path("login/", LoginView.as_view()),
    path("send-otp/", SendOTpView.as_view()),
    path("verify-otp/", VerifyOtpView.as_view()),
    path("", include(router.urls)),
]