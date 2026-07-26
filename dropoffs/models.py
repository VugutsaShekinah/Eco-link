"""
dropoffs/models.py — the DropOff record (report Appendix 2 + §3.2.3.2).

A DropOff is a single, timestamped plastic deposit made by a user at a hub.
It is created as PENDING and only awards eco-points once an administrator marks
it VERIFIED — enforced by a post_save signal in dropoffs/signals.py.
"""

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from hubs.models import Hub

from . import points


class DropOff(models.Model):
    """One plastic deposit: who, where, what type, how much, and its status."""

    class PlasticType(models.TextChoices):
        BAGS = "BAGS", "Plastic Bags"
        BOTTLES = "BOTTLES", "Bottles / Containers"
        HARD = "HARD", "Hard Plastics"
        MIXED = "MIXED", "Mixed Plastics"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        VERIFIED = "VERIFIED", "Verified"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dropoffs",
    )
    hub = models.ForeignKey(
        Hub,
        on_delete=models.PROTECT,   # keep history: don't delete a hub with drop-offs
        related_name="dropoffs",
    )
    plastic_type = models.CharField(max_length=10, choices=PlasticType.choices)
    weight_kg = models.DecimalField(
        "weight (kg)",
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],   # reject zero/negative weights
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]          # newest first
        indexes = [
            models.Index(fields=["user", "status"]),   # fast dashboard/history queries
        ]

    def __str__(self):
        return f"{self.user} · {self.weight_kg}kg {self.get_plastic_type_display()} ({self.get_status_display()})"

    def calculate_points(self):
        """Eco-points this drop-off is worth, via the single shared formula."""
        return points.calculate_points(self.weight_kg)

    @property
    def is_verified(self):
        return self.status == self.Status.VERIFIED
