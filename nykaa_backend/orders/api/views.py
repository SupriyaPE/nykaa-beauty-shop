from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from cart.models import CartItem
from orders.models import Order, OrderItem
from cart.api.views import get_or_create_cart
from addresses.models import Address
from django.conf import settings


# --------------------------------------------------
# CREATE ORDER (GUEST + AUTH USER)
# --------------------------------------------------
@api_view(["POST"])
@permission_classes([AllowAny])
def create_order(request):
    """
    Nykaa-style order creation
    - Works for BOTH guest and authenticated users
    - No re-authentication here
    """

    user = request.user if request.user.is_authenticated else None
    guest_id = request.COOKIES.get("guest_id")

    # 🛒 CART
    cart = get_or_create_cart(request)
    if not cart:
        return Response({"error": "Cart not found"}, status=400)

    cart_items = CartItem.objects.filter(cart=cart)
    if not cart_items.exists():
        return Response({"error": "Cart empty"}, status=400)

    # 📍 ADDRESS
    address_id = request.data.get("address_id")

    if address_id and user:
        try:
            addr = Address.objects.get(id=address_id, user=user)
            address_json = {
                "name": addr.name,
                "mobile": addr.mobile,
                "address_line": addr.address_line,
                "city": addr.city,
                "state": addr.state,
                "pincode": addr.pincode,
            }
        except Address.DoesNotExist:
            return Response({"error": "Invalid address"}, status=400)
    else:
        address_json = {
            "name": request.data.get("name"),
            "mobile": request.data.get("mobile"),
            "address_line": request.data.get("address_line"),
            "city": request.data.get("city"),
            "state": request.data.get("state"),
            "pincode": request.data.get("pincode"),
        }

    if not all(address_json.values()):
        return Response({"error": "Incomplete address"}, status=400)
    
    # 🚚 DELIVERY VALIDATION (PRODUCT-WISE)
    user_state = address_json.get("state").strip().lower()
    user_pincode = address_json.get("pincode").strip()

    for item in cart_items:
        variant = item.product_variant
        scope = variant.delivery_scope
        value = variant.delivery_value or ""

        values = [v.strip().lower() for v in value.split(",") if v.strip()]

        deliverable = True

        if scope == "STATE_ONLY":
            deliverable = user_state in values

        elif scope == "STATE_EXCEPT":
            deliverable = user_state not in values

        elif scope == "PINCODE_ONLY":
            deliverable = user_pincode in values

        elif scope == "PINCODE_EXCEPT":
            deliverable = user_pincode not in values

        if not deliverable:
            return Response(
                {
                    "error": f"{variant.product.name} is not deliverable to your location"
                },
                status=400
            )

    # 💰 TOTAL
    total_amount = sum(
        item.quantity * item.product_variant.selling_price
        for item in cart_items
    )

    
    # 🚚 CALCULATE EXPECTED DELIVERY DAYS
    expected_delivery_days = 0

    for item in cart_items:
        variant_days = item.product_variant.base_delivery_days
        if variant_days > expected_delivery_days:
            expected_delivery_days = variant_days


    # ✅ CREATE ORDER
    order = Order.objects.create(
        user=user,
        guest_id=None if user else guest_id,
        address_json=address_json,
        total_amount=total_amount,
        payment_status="PENDING",
        order_status="CREATED",
        expected_delivery_days=expected_delivery_days, 
    )

    # 📦 ORDER ITEMS
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product_variant=item.product_variant,
            quantity=item.quantity,
            price=item.product_variant.selling_price,
        )

    return Response({"order_id": order.id}, status=200)


# --------------------------------------------------
# MY ORDERS (AUTH USER ONLY)
# --------------------------------------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_orders(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by("-created_at")

    response = []

    for order in orders:
        items_data = []

        for item in order.items.all():
            review = item.product_variant.reviews.filter(
                user=user,
                order=order
            ).first()

            items_data.append({
                "variant_id": item.product_variant.id,
                "product_name": item.product_variant.product.name,
                "variant_name": item.product_variant.variant_name,
                "reviewed": bool(review),
                "rating": review.rating if review else None
            })

        response.append({
            "id": order.id,
            "total_amount": str(order.total_amount),
            "payment_status": order.payment_status,
            "order_status": order.order_status,
            "created_at": order.created_at,
            "expected_delivery_days": order.expected_delivery_days,
            "items": items_data
        })

    return Response(response, status=200)

  
  
  # --------------------------------------------------
# GET ORDER SUMMARY (PAYMENT PAGE)
# --------------------------------------------------
@api_view(["GET"])
@permission_classes([AllowAny])
def get_order_summary(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=404)

    items_count = 0
    total_mrp = 0
    total_pay = 0

    for item in order.items.all():
        items_count += item.quantity
        total_mrp += item.price * item.quantity
        total_pay += item.price * item.quantity

    savings = total_mrp - total_pay

    return Response({
        "items_count": items_count,
        "total_mrp": float(total_mrp),
        "total_pay": float(total_pay),
        "savings": float(savings),
    })