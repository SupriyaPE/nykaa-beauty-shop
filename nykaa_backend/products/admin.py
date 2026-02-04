from django.contrib import admin
from .models import (
    Category,
    Brand,
    Banner,
    Offer,
    Product,
    ProductVariant,
    ProductImage,
)


# =========================
# CATEGORY ADMIN
# =========================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "is_active")
    list_filter = ("is_active",)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


# =========================
# BRAND ADMIN
# =========================
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


# =========================
# BANNER ADMIN
# =========================
@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("title", "banner_type", "position", "is_active")
    list_filter = ("banner_type", "is_active")
    ordering = ("position",)


# =========================
# OFFER ADMIN
# =========================
@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ("title", "discount_percent", "is_active")
    list_filter = ("is_active",)


# =========================
# PRODUCT IMAGE INLINE
# =========================
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


# =========================
# PRODUCT VARIANT ADMIN
# =========================
@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("product", "variant_name", "selling_price", "stock", "is_active")
    list_filter = ("is_active",)
    inlines = [ProductImageInline]


# =========================
# PRODUCT ADMIN
# =========================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "category", "is_active", "is_featured")
    list_filter = ("brand", "category", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
