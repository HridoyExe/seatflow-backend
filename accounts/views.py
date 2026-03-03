from rest_framework import viewsets
from .models import User, OTP
from .serializers import UserSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status

User = get_user_model()

class LoginView(APIView):

    def post(self, request):
        identifier = request.data.get("identifier")
        password = request.data.get("password")

        if not identifier or not password:
            return Response(
                {"error": "Identifier and password required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Email Login
        if "@" in identifier:
            user = User.objects.filter(email=identifier).first()

            if not user:
                return Response({"error": "User not found"})

            if not user.is_verified:
                return Response({"error": "Email not verified"})

        # Phone Login
        else:
            user = User.objects.filter(phone=identifier).first()

            if not user:
                return Response({"error": "User not found"})

    
        if not user.check_password(password):
            return Response({"error": "Invalid credentials"})

        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        })
class SendOTpView(APIView):

    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response(
                {"error": "Email Required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.filter(email=email).first()

        if not user:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Delete old OTP
        OTP.objects.filter(user=user, is_used=False).delete()

        # Create new OTP
        otp = OTP.objects.create(user=user)

        # Send Email
        send_mail(
            subject="Your Verification OTP",
            message=f"Your OTP code is {otp.code}. Valid for 5 minutes.",
            from_email=None,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response(
            {"message": "OTP sent successfully"},
            status=status.HTTP_200_OK
        )

class VerifyOtpView(APIView):

    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("code")

        if not email or not code:
            return Response(
                {"error": "Email and code required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.filter(email=email).first()

        if not user:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        otp = OTP.objects.filter(
            user=user,
            code=code,
            is_used=False
        ).first()

        if not otp:
            return Response(
                {"error": "Invalid OTP"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if otp.is_expire():
            return Response(
                {"error": "OTP expired"},
                status=status.HTTP_400_BAD_REQUEST
            )

        otp.is_used = True
        otp.save()

        user.is_verified = True
        user.save()

        return Response(
            {"message": "Email verified successfully"},
            status=status.HTTP_200_OK
        )
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer