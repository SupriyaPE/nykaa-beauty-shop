from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
import random

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import UserOTP
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .serializers import ProfileSerializer

UserModel = get_user_model()

OTP_EXPIRY_MINUTES = 5


# --------------------------------------------------
# SEND OTP
# --------------------------------------------------
@api_view(["POST"])
def send_otp(request):
    email = request.data.get("email")

    if not email:
        return Response({"error": "Email required"}, status=400)

    # Check user existence
    user = UserModel.objects.filter(email=email).first()
    is_new_user = False

    if not user:
        # Create inactive user for signup flow
        user = UserModel.objects.create(
            email=email,
            full_name="",
            is_active=True
        )
        is_new_user = True

    # ⛔ RATE LIMIT (1 OTP per 60 seconds)
    recent_otp = UserOTP.objects.filter(
        user=user,
        created_at__gte=timezone.now() - timedelta(seconds=60)
    ).first()

    if recent_otp:
        return Response(
            {"error": "Please wait before requesting another OTP"},
            status=429
        )

    # Generate OTP
    otp = random.randint(100000, 999999)

    # Invalidate old OTPs
    UserOTP.objects.filter(user=user, is_used=False).update(is_used=True)

    # Save OTP in DB
    UserOTP.objects.create(
        user=user,
        otp=str(otp),
        otp_type="LOGIN"
    )

    # 🔥 SEND OTP EMAIL
    try:
        send_mail(
            subject="Your Nykaa OTP",
            message=f"Your OTP is {otp}. It is valid for 5 minutes.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception:
        return Response(
            {"error": "Failed to send OTP email"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # 🔒 DEV SAFETY LOG
    print("OTP FOR", email, ":", otp)

    return Response({
        "message": "OTP sent",
        "is_new_user": is_new_user
    })

# --------------------------------------------------
# VERIFY OTP
# --------------------------------------------------
@api_view(["POST"])
def verify_otp(request):
    email = request.data.get("email")
    otp = request.data.get("otp")

    if not email or not otp:
        return Response(
            {"error": "Email and OTP required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = UserModel.objects.filter(email=email).first()
    if not user:
        return Response({"error": "User not found"}, status=404)

    otp_obj = UserOTP.objects.filter(
        user=user,
        otp=str(otp),
        is_used=False
    ).order_by("-created_at").first()

    if not otp_obj:
        return Response({"error": "Invalid OTP"}, status=400)

    # ⏱ OTP EXPIRY (5 minutes)
    if timezone.now() > otp_obj.created_at + timedelta(minutes=5):
        return Response({"error": "OTP expired"}, status=400)

    # Mark OTP as used
    otp_obj.is_used = True
    otp_obj.save()

    # Check if user completed signup
    is_new_user = not bool(user.full_name)

    # Existing user → issue tokens
    if not is_new_user:
        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "is_new_user": False,
            "user": {
                "id": user.id,
                "name": user.full_name,
                "email": user.email
            }
        })

    # New user → frontend asks name
    return Response({
        "is_new_user": True
    })
# --------------------------------------------------
# COMPLETE SIGNUP (NEW USER)
# --------------------------------------------------
@api_view(["POST"])
def complete_signup(request):
    email = request.data.get("email")
    full_name = request.data.get("full_name")

    if not email or not full_name:
        return Response(
            {"error": "Email and full name required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = UserModel.objects.get(email=email)
    except UserModel.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Update user name
    user.full_name = full_name
    user.save(update_fields=["full_name"])

    # Mark OTP as used
    UserOTP.objects.filter(
        user=user,
        is_used=False
    ).update(is_used=True)

    refresh = RefreshToken.for_user(user)

    return Response({
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": {
            "id": user.id,
            "name": user.full_name,
            "email": user.email,
        }
    })

# --------------------------------------------------
# LOGOUT
# --------------------------------------------------
@api_view(["POST"])
def logout(request):
    response = Response({"message": "Logged out successfully"})

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    response.delete_cookie("guest_id")

    return response




# --------------------------------------------------
# PROFILE VIEW
# --------------------------------------------------
@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def profile_view(request):
    user = request.user

    if request.method == "GET":
        serializer = ProfileSerializer(user)
        return Response(serializer.data)

    if request.method == "PATCH":
        serializer = ProfileSerializer(
            user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)    