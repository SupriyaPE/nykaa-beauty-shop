from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def toggle_wishlist(request):
    variant_id = request.data.get("variant_id")

    if not variant_id:
        return Response({"error": "Variant ID required"}, status=400)

    from products.models import ProductVariant
    from wishlist.models import Wishlist

    try:
        variant = ProductVariant.objects.get(id=variant_id)
    except ProductVariant.DoesNotExist:
        return Response({"error": "Invalid variant"}, status=404)

    wishlist_item = Wishlist.objects.filter(
        user=request.user,
        product_variant=variant
    ).first()

    if wishlist_item:
        wishlist_item.delete()
        return Response({"added": False})

    Wishlist.objects.create(
        user=request.user,
        product_variant=variant
    )
    return Response({"added": True})



from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from wishlist.models import Wishlist


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def wishlist_list(request):
    items = Wishlist.objects.filter(user=request.user).select_related(
        "product_variant",
        "product_variant__product"
    )

    data = []
    for item in items:
        variant = item.product_variant
        product = variant.product

        data.append({
            "id": item.id,
            "variant_id": variant.id,
            "product_name": product.name,
            "brand": product.brand.name,
            "price": variant.selling_price,
            "mrp": variant.mrp,
            "image": variant.images.first().image.url if variant.images.first() else "",
            "slug": product.slug,
        })

    return Response(data)


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def wishlist_ids(request):
    ids = Wishlist.objects.filter(
        user=request.user
    ).values_list("product_variant_id", flat=True)

    return Response(list(ids))    