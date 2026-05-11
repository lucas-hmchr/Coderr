from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    """Represents a user's profile (customer or business)."""
    CUSTOMER = "customer"
    BUSINESS = "business"

    USER_TYPE_CHOICES = [
        (CUSTOMER, "Customer"),
        (BUSINESS, "Business"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        primary_key=True,
    )
    file = models.FileField(upload_to="profiles/", blank=True, null=True)
    location = models.CharField(max_length=255, blank=True)
    tel = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    working_hours = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "User profile"
        verbose_name_plural = "User profiles"
        ordering = ["user__username"]

    def __str__(self):
        return f"{self.user.username} ({self.type})"