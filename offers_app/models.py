from django.db import models
from django.conf import settings

class Offer(models.Model):
    """Represents a service offer."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="offers")
    title = models.CharField(max_length=255)
    image = models.FileField(upload_to="offers/", blank=True, null=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Offer"
        verbose_name_plural = "Offers"
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title


class OfferDetail(models.Model):
    """Details (packages) of a service offer."""
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"

    OFFER_TYPE_CHOICES = [
        (BASIC, "Basic"),
        (STANDARD, "Standard"),
        (PREMIUM, "Premium"),
    ]

    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name="details",
    )
    title = models.CharField(max_length=255)
    revisions = models.IntegerField()
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPE_CHOICES)

    class Meta:
        verbose_name = "Offer detail"
        verbose_name_plural = "Offer details"
        ordering = ["price"]
        constraints = [
            models.UniqueConstraint(
                fields=["offer", "offer_type"],
                name="unique_offer_type_per_offer",
            )
        ]

    def __str__(self):
        return f"{self.offer.title} - {self.offer_type}"