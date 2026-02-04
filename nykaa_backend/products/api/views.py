from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from orders.models import Order, OrderItem

from products.models import (
    Category,
    Brand,
    Banner,
    Product,
    ProductVariant,
    ProductImage,
)

from .serializers import (
    CategorySerializer,
    BrandSerializer,
    BannerSerializer,
    ProductSerializer,
    ProductVariantSerializer,
    ProductImageSerializer,
)


# ===============================
# CATEGORY CRUD
# ===============================
class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


# ===============================
# BRAND CRUD
# ===============================
class BrandViewSet(ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAuthenticated]


# ===============================
# BANNER CRUD
# ===============================
class BannerViewSet(ModelViewSet):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    permission_classes = [IsAuthenticated]


# ===============================
# PRODUCT CRUD
# ===============================
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]   # frontend can read


# ===============================
# PRODUCT VARIANT CRUD
# ===============================
class ProductVariantViewSet(ModelViewSet):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer
    permission_classes = [IsAuthenticated]


# ===============================
# PRODUCT IMAGE CRUD
# ===============================
class ProductImageViewSet(ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [IsAuthenticated]




# ==================================================
# CHECK PRODUCT DELIVERY BY PINCODE (PRODUCT PAGE)
# ==================================================

def get_state_from_pincode(pincode):
    p = int(pincode)

    if 670000 <= p <= 695999:
        return "kerala"
    if 560000 <= p <= 591999:
        return "karnataka"
    if 600000 <= p <= 679999:
        return "tamil nadu"
    if 500000 <= p <= 539999:
        return "andhra pradesh"
    if 400000 <= p <= 499999:
        return "maharashtra"

    return None


@api_view(["POST"])
@permission_classes([AllowAny])
def check_product_delivery(request):
    variant_id = request.data.get("variant_id")
    pincode = request.data.get("pincode")

    if not variant_id or not pincode:
        return Response(
            {"error": "variant_id and pincode are required"},
            status=400
        )

    if not str(pincode).isdigit() or len(str(pincode)) != 6:
        return Response(
            {"error": "Invalid pincode"},
            status=400
        )

    try:
        variant = ProductVariant.objects.get(id=variant_id, is_active=True)
    except ProductVariant.DoesNotExist:
        return Response({"error": "Invalid product variant"}, status=404)

    # 🔑 Convert PINCODE → STATE
    user_state = get_state_from_pincode(pincode)

    if not user_state:
        return Response(
            {
                "deliverable": False,
                "message": "Delivery not available to this location"
            },
            status=200
        )

    user_state = user_state.lower()
    user_pincode = str(pincode)

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
                "deliverable": False,
                "message": "This product is not deliverable to your location"
            },
            status=200
        )

    return Response(
        {
            "deliverable": True,
            "eta_days": variant.base_delivery_days,
            "message": f"Delivered in {variant.base_delivery_days} days"
        },
        status=200
    )




from orders.models import OrderItem
from products.models import ProductReview
from rest_framework.permissions import IsAuthenticated

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def submit_review(request):
    user = request.user
    variant_id = request.data.get("variant_id")
    order_id = request.data.get("order_id")
    rating = request.data.get("rating")
    comment = request.data.get("comment", "")

    if not all([variant_id, order_id, rating]):
        return Response({"error": "Missing fields"}, status=400)

    # ✅ Order must be delivered
    try:
        order = Order.objects.get(
            id=order_id,
            user=user,
            order_status="DELIVERED"
        )
    except Order.DoesNotExist:
        return Response(
            {"error": "Order not eligible for review"},
            status=400
        )

    # ✅ Product must exist in order
    exists = OrderItem.objects.filter(
        order=order,
        product_variant_id=variant_id
    ).exists()

    if not exists:
        return Response(
            {"error": "Product not in this order"},
            status=400
        )

    # ✅ Create review
    ProductReview.objects.create(
        user=user,
        product_variant_id=variant_id,
        order=order,
        rating=rating,
        comment=comment
    )

    return Response({"status": "Review submitted"}, status=201)






from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from products.models import Product, ProductReview
from .serializers import ProductReviewListSerializer
from django.db.models import Avg


@api_view(["GET"])
@permission_classes([AllowAny])
def product_reviews(request, product_id):
    try:
        product = Product.objects.get(id=product_id, is_active=True)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)

    reviews = ProductReview.objects.filter(
        product_variant__product=product
    ).select_related("user")

    avg_rating = reviews.aggregate(avg=Avg("rating"))["avg"] or 0

    serializer = ProductReviewListSerializer(reviews, many=True)

    return Response({
        "average_rating": round(avg_rating, 1),
        "total_reviews": reviews.count(),
        "reviews": serializer.data
    }, status=200)