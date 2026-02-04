from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import SignupSerializer

from django.contrib.auth import get_user_model
import random

UserModel = get_user_model()

# ===============================
# TEMP OTP STORE (DEV ONLY)
# ===============================
OTP_STORE = {}


# --------------------------------------------------
# LOGIN (PASSWORD)
# --------------------------------------------------
@api_view(["POST"])
def login(request):
    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response(
            {"non_field_errors": ["Email and password are required"]},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(email=email, is_active=True)
    except User.DoesNotExist:
        return Response(
            {"non_field_errors": ["Invalid email or password"]},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not check_password(password, user.password):
        return Response(
            {"non_field_errors": ["Invalid email or password"]},
            status=status.HTTP_400_BAD_REQUEST
        )

    refresh = RefreshToken.for_user(user)

  
    return Response({
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": {
            "id": user.id,
            "name": user.get_full_name(),
            "email": user.email
        }
    })


# --------------------------------------------------
# SIGNUP
# --------------------------------------------------
@api_view(["POST"])
def signup_view(request):
    serializer = SignupSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = serializer.save()
    refresh = RefreshToken.for_user(user)

    return Response({
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": {
            "id": user.id,
            "name": user.get_full_name(),
            "email": user.email
        }
    }, status=status.HTTP_201_CREATED)


# --------------------------------------------------
# SEND OTP
# --------------------------------------------------
@api_view(["POST"])
def send_otp(request):
    email = request.data.get("email")

    if not email:
        return Response({"error": "Email required"}, status=400)

    otp = random.randint(100000, 999999)
    OTP_STORE[email] = otp

    user, created = UserModel.objects.get_or_create(
        email=email,
        defaults={
            "full_name": email.split("@")[0],
            "is_active": True
        }
    )

    print("OTP FOR", email, ":", otp)  # DEV ONLY

    return Response({
        "message": "OTP sent",
        "is_new_user": created
    })

# --------------------------------------------------
# VERIFY OTP (LOGIN)
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

    if str(OTP_STORE.get(email)) != str(otp):
        return Response(
            {"error": "Invalid OTP"},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = UserModel.objects.get(email=email)
    refresh = RefreshToken.for_user(user)

    del OTP_STORE[email]

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

    # 🔥 JWT cleanup (frontend also clears localStorage)
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    # 🔥 Start fresh guest session
    response.delete_cookie("guest_id")

    return response