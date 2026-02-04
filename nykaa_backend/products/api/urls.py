from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    BrandViewSet,
    BannerViewSet,
    ProductViewSet,
    ProductVariantViewSet,
    ProductImageViewSet,
    check_product_delivery,
    submit_review,
    product_reviews,
)

router = DefaultRouter()
router.register("categories", CategoryViewSet)
router.register("brands", BrandViewSet)
router.register("banners", BannerViewSet)
router.register("products", ProductViewSet)
router.register("variants", ProductVariantViewSet)
router.register("images", ProductImageViewSet)

urlpatterns = [
    # 🔍 Custom delivery check API
    path("products/check-delivery/", check_product_delivery),
    path("products/reviews/submit/", submit_review),
    path("products/<int:product_id>/reviews/", product_reviews),
]

# 🔗 Add router URLs
urlpatterns += router.urls