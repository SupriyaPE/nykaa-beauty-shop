from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from addresses.models import Address
from accounts.models import User
from .serializers import AddressSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication


@api_view(["GET", "POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([AllowAny])
def address_list_create(request):

    # =====================
    # GET → LIST ADDRESSES
    # =====================
    if request.method == "GET":
        if not request.user.is_authenticated:
            return Response([], status=200)

        user = User.objects.filter(id=request.user.id).first()
        if not user:
            return Response([], status=200)

        addresses = Address.objects.filter(user=user).order_by("-id")
        serializer = AddressSerializer(addresses, many=True)
        return Response(serializer.data, status=200)

    # =====================
    # POST → SAVE ADDRESS
    # =====================
    data = request.data

    required = ["name", "mobile", "address_line", "city", "state", "pincode"]
    for field in required:
        if not data.get(field):
            return Response({"error": f"{field} required"}, status=400)

    if request.user.is_authenticated:
        user = User.objects.filter(id=request.user.id).first()
        if user:
            Address.objects.create(
                user=user,
                name=data["name"],
                mobile=data["mobile"],
                address_line=data["address_line"],
                city=data["city"],
                state=data["state"],
                pincode=data["pincode"],
            )
            return Response({"status": "saved"}, status=201)

    # guest fallback (do nothing)
    return Response({"status": "saved"}, status=201)