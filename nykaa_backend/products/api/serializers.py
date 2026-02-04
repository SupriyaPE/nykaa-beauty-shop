from rest_framework import serializers
from products.models import (
    Category,
    Brand,
    Banner,
    Product,
    ProductVariant,
    ProductImage,
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = "__all__"


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = "__all__"


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = "__all__"


class ProductVariantSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = ProductVariant
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = "__all__"




from products.models import ProductReview
from rest_framework import serializers


class ProductReviewListSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.email")

    class Meta:
        model = ProductReview
        fields = [
            "user",
            "rating",
            "comment",
            "created_at",
        ]        