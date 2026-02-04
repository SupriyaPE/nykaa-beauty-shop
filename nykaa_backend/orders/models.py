from django.db import models
from django.conf import settings
from products.models import ProductVariant
import uuid


class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )

    guest_id = models.UUIDField(null=True, blank=True)

    address_json = models.JSONField(null=True, blank=True)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    expected_delivery_days = models.PositiveIntegerField(default=0)
    payment_status = models.CharField(max_length=20)
    order_status = models.CharField(max_length=20)

    razorpay_order_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id}"




class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name="items",
        on_delete=models.CASCADE
    )

    product_variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_variant} x {self.quantity}"