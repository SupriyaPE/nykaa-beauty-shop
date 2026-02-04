from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.conf import settings

# =========================
# CATEGORY
# =========================
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children"
    )


    # HEADER CONTROL (NYKAA STYLE)
    show_in_header = models.BooleanField(default=True)
    header_order = models.PositiveIntegerField(default=0)
    is_luxe = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["header_order", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# =========================
# BRAND
# =========================
class Brand(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    logo = models.ImageField(upload_to="brands/", blank=True, null=True)

    is_luxe = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# =========================
# BANNER (HOME PAGE)
# =========================
class Banner(models.Model):
    BANNER_TYPES = (
        ("hero", "Hero Banner"),
        ("offer", "Offer Banner"),
        ("strip", "Strip Banner"),
    )

    title = models.CharField(max_length=150)
    image = models.ImageField(upload_to="banners/")
    banner_type = models.CharField(max_length=20, choices=BANNER_TYPES)
    position = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return f"{self.title} ({self.banner_type})"


# =========================
# OFFER
# =========================
class Offer(models.Model):
    title = models.CharField(max_length=150)
    discount_percent = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


# =========================
# PRODUCT
# =========================
class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)

    brand = models.ForeignKey(
        Brand,
        on_delete=models.PROTECT,
        related_name="products"
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products"
    )

    description = models.TextField(blank=True)

    offer = models.ForeignKey(
        Offer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# =========================
# PRODUCT VARIANT (SHADE / SIZE)
# =========================
class ProductVariant(models.Model):
    DELIVERY_SCOPE_CHOICES = (
        ("ALL_INDIA", "All India"),
        ("STATE_ONLY", "Only Selected States"),
        ("STATE_EXCEPT", "All Except Selected States"),
        ("PINCODE_ONLY", "Only Selected Pincodes"),
        ("PINCODE_EXCEPT", "All Except Selected Pincodes"),
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants"
    )

    variant_name = models.CharField(
        max_length=100,
        help_text="Shade / Size / Pack"
    )

    sku = models.CharField(max_length=100, unique=True)
    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)

    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    # ✅ PRODUCT-WISE DELIVERY AVAILABILITY
    delivery_scope = models.CharField(
        max_length=20,
        choices=DELIVERY_SCOPE_CHOICES,
        default="ALL_INDIA"
    )

   
    delivery_value = models.TextField(
        blank=True,
        null=True
    )

    # ✅ BASE DELIVERY TIME (DAYS)
    base_delivery_days = models.PositiveIntegerField(
        default=3
    )

    def __str__(self):
        return f"{self.product.name} - {self.variant_name}"


# =========================
# PRODUCT IMAGES
# =========================
class ProductImage(models.Model):
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.ImageField(upload_to="products/")
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.variant}"



# =========================
# PRODUCT Review
# =========================

from django.conf import settings
from orders.models import Order

class ProductReview(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    product_variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE
    )

    rating = models.PositiveIntegerField()  # 1–5
    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product_variant", "order")

    def __str__(self):
        return f"{self.product_variant} - {self.rating}⭐"      