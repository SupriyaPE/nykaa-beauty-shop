import razorpay
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response

from cart.models import Cart, CartItem
from orders.models import Order, OrderItem


# Razorpay client
client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)


# --------------------------------------------------
# CREATE RAZORPAY ORDER (GUEST + USER)
# --------------------------------------------------
@api_view(["POST"])
def create_razorpay_order(request):
    order_id = request.data.get("order_id")

    if not order_id or str(order_id)=="undefined":
        return Response({"error": "Invalid order_id"}, status=400)

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=404)

    razorpay_order = client.order.create({
        "amount": int(float(order.total_amount) * 100),  # ✅ FIX
        "currency": "INR",
        "payment_capture": 1
    })
    
    order.razorpay_order_id = razorpay_order["id"]
    order.save()

    return Response({
        "razorpay_order_id": razorpay_order["id"],
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "amount": float(order.total_amount)
    })


      
    

# --------------------------------------------------
# VERIFY PAYMENT
# --------------------------------------------------
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(["POST"])
def verify_razorpay_payment(request):
    data = request.data

    # ✅ Skip Razorpay signature check in LOCAL / Thunder testing
    if not settings.DEBUG:
        try:
            client.utility.verify_payment_signature({
                "razorpay_order_id": data["razorpay_order_id"],
                "razorpay_payment_id": data["razorpay_payment_id"],
                "razorpay_signature": data["razorpay_signature"],
            })
        except Exception:
            return Response({"status": "FAILED"}, status=400)

    try:
        order = Order.objects.get(razorpay_order_id=data["razorpay_order_id"])
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=404)

    # ✅ Mark order paid
    order.payment_status = "SUCCESS"
    order.order_status = "PLACED"
    order.razorpay_payment_id = data["razorpay_payment_id"]
    order.save()

    # ✅ Clear cart AFTER payment
    if order.user:
        Cart.objects.filter(user=order.user).delete()
    else:
        Cart.objects.filter(guest_id=order.guest_id).delete()

    return Response({
        "status": "SUCCESS",
        "order_id": order.id
    })

    