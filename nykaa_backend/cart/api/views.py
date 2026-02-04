import uuid
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from cart.models import Cart, CartItem
from products.models import ProductVariant


# ==================================================
# HELPER: GET OR CREATE CART (NYKAA STYLE)
# ==================================================
def get_or_create_cart(request):
    """
    Rules:
    - Guest → cookie based cart
    - Logged in user → ONE persistent cart
    - Guest cart MERGES into user cart on login
    """

    # =============================
    # AUTHENTICATED USER
    # =============================
    if request.user.is_authenticated:

        # 🔒 Always reuse existing user cart
        user_cart = (
            Cart.objects
            .filter(user=request.user)
            .order_by("created_at")
            .first()
        )

        if not user_cart:
            user_cart = Cart.objects.create(
                user=request.user,
                guest_id=None
            )

        guest_id = request.COOKIES.get("guest_id")

        if guest_id:
            try:
                guest_cart = Cart.objects.get(
                    guest_id=guest_id,
                    user__isnull=True
                )

                # 🔥 MERGE guest items into user cart
                for item in guest_cart.items.all():
                    user_item, created = CartItem.objects.get_or_create(
                        cart=user_cart,
                        product_variant=item.product_variant,
                        defaults={"quantity": item.quantity}
                    )
                    if not created:
                        user_item.quantity += item.quantity
                        user_item.save()

                # 🔥 DELETE guest cart
                guest_cart.delete()

                # 🔥 SIGNAL to delete cookie
                request.delete_guest_cookie = True

            except Cart.DoesNotExist:
                pass

        return user_cart

    # =============================
    # GUEST USER
    # =============================
    guest_id = request.COOKIES.get("guest_id")

    if not guest_id:
        guest_id = str(uuid.uuid4())
        request.new_guest_id = guest_id

    cart, _ = Cart.objects.get_or_create(
        guest_id=guest_id,
        user__isnull=True
    )

    return cart


# ==================================================
# VIEW CART
# ==================================================
@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([AllowAny])
def view_cart(request):
    cart = get_or_create_cart(request)

    items = cart.items.all()
    total = sum(i.subtotal() for i in items)

    response = Response({
        "items": [
            {
                "id": i.id,
                "product": i.product_variant.product.name,
                "variant": i.product_variant.variant_name,
                "quantity": i.quantity,
                "price": float(i.product_variant.selling_price),
                "subtotal": float(i.subtotal()),
            }
            for i in items
        ],
        "total": float(total)
    })

    if hasattr(request, "new_guest_id"):
        response.set_cookie(
            "guest_id",
            request.new_guest_id,
            max_age=60 * 60 * 24 * 30,
            httponly=True,
            samesite="Lax"
        )

    if hasattr(request, "delete_guest_cookie"):
        response.delete_cookie("guest_id")

    return response


# ==================================================
# ADD TO CART
# ==================================================
@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([AllowAny])
def add_to_cart(request):
    cart = get_or_create_cart(request)

    variant_id = request.data.get("variant_id")
    if not variant_id:
        return Response({"error": "variant_id required"}, status=400)

    try:
        variant = ProductVariant.objects.get(id=variant_id)
    except ProductVariant.DoesNotExist:
        return Response({"error": "Invalid variant"}, status=404)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product_variant=variant,
        defaults={"quantity": 1}
    )

    if not created:
        item.quantity += 1
        item.save()

    response = Response({"message": "Added to bag"})

    if hasattr(request, "new_guest_id"):
        response.set_cookie("guest_id", request.new_guest_id)

    if hasattr(request, "delete_guest_cookie"):
        response.delete_cookie("guest_id")

    return response


# ==================================================
# UPDATE QUANTITY
# ==================================================
@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([AllowAny])
def update_quantity(request):
    item_id = request.data.get("item_id")
    action = request.data.get("action")

    item = CartItem.objects.get(id=item_id)

    if action == "increase":
        item.quantity += 1
    elif action == "decrease" and item.quantity > 1:
        item.quantity -= 1

    item.save()
    return Response({"message": "Updated"})


# ==================================================
# REMOVE ITEM
# ==================================================
@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([AllowAny])
def remove_item(request):
    CartItem.objects.filter(id=request.data.get("item_id")).delete()
    return Response({"message": "Removed"})