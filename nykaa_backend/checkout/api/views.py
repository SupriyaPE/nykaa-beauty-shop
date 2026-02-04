# checkout/api/views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from cart.models import Cart
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import authentication_classes

@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([AllowAny])
def checkout_account_status(request):
    """
    Nykaa-style checkout account step
    JWT based (NO session auth)
    """

    jwt_auth = JWTAuthentication()
    user_auth = jwt_auth.authenticate(request)

    # 🔐 LOGGED-IN USER (JWT PRESENT)
    if user_auth:
        user, token = user_auth
        return Response({
            "status": "LOGGED_IN",
            "next": "ADDRESS",
            "user_id": user.id
        })

    # 👤 GUEST USER
    guest_id = request.COOKIES.get("guest_id")

    if not guest_id:
        return Response({
            "status": "EMPTY",
            "message": "No cart found"
        })

    cart = Cart.objects.filter(guest_id=guest_id).first()

    if not cart or not cart.items.exists():
        return Response({
            "status": "EMPTY",
            "message": "Cart is empty"
        })

    return Response({
        "status": "GUEST",
        "next": "ADDRESS_FORM",  # 👈 important for frontend logic
    })



@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([AllowAny])
def save_guest_address(request):
    """
    Nykaa-style guest address:
    - Stored in session
    - No DB
    - No JWT
    """

    data = {
        "name": request.data.get("name"),
        "mobile": request.data.get("mobile"),
        "address_line": request.data.get("address_line"),
        "city": request.data.get("city"),
        "state": request.data.get("state"),
        "pincode": request.data.get("pincode"),
    }

    
    if not all(data.values()):
        return Response(
            {"error": "All address fields are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # ✅ Save in session
    request.session["guest_address"] = data
    request.session.modified = True

    return Response({
        "message": "Guest address saved successfully"
    })


