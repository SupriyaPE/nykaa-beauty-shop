from django.db import models
from django.conf import settings
from products.models import ProductVariant
import uuid


class Cart(models.Model):
    """
    One active cart per user OR guest
    Matches Order model (UUID based)
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    # UUID for guest (same concept used in Order)
    guest_id = models.UUIDField(
        default=uuid.uuid4,
        null=True,
        blank=True,
        db_index=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["guest_id"]),
        ]

    def __str__(self):
        return f"Cart {self.id}"



class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        related_name="items",
        on_delete=models.CASCADE
    )

    product_variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("cart", "product_variant")

    def subtotal(self):
        return self.quantity * self.product_variant.selling_price

    def __str__(self):
        return f"{self.product_variant} x {self.quantity}"