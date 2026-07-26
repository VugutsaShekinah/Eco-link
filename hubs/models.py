"""
hubs/models.py — collection infrastructure for ECO-LINK.

Two entities from the report's ERD (§3.3.3):

- Hub          : a physical collection point on/around campus where users deposit
                 plastic. Stores name, location, capacity, and operational status.
- Manufacturer : a certified recycler that takes custody of verified plastic from
                 hubs (§3.3.3, §5.4.3). External stakeholder — no login (§1.5).
"""

from django.core.validators import MinValueValidator
from django.db import models


class Manufacturer(models.Model):
    """A certified recycling company that collects verified plastic from hubs."""

    name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=255, blank=True)
    # What this recycler accepts — free text keeps it flexible for a demo.
    materials_accepted = models.CharField(
        max_length=255,
        blank=True,
        help_text="Plastic types this recycler accepts, e.g. 'Bottles, Hard plastics'.",
    )
    is_certified = models.BooleanField(
        default=True,
        help_text="Whether this recycler is currently vetted/certified.",
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Hub(models.Model):
    """A designated collection point where plastic is deposited and weighed."""

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"          # open and accepting drop-offs
        FULL = "FULL", "Full"                # at capacity, awaiting pickup
        CLOSED = "CLOSED", "Closed"          # temporarily not accepting
        MAINTENANCE = "MAINTENANCE", "Under maintenance"

    name = models.CharField(max_length=120)
    location = models.CharField(
        max_length=255,
        help_text="Where the hub is, e.g. 'Main Cafeteria entrance'.",
    )
    # Maximum plastic the hub can hold before it needs a manufacturer pickup.
    capacity_kg = models.DecimalField(
        "capacity (kg)",
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Maximum kilograms the hub can hold before pickup.",
    )
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    # Manufacturer responsible for collecting from this hub.
    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hubs",
        help_text="Certified recycler that collects from this hub.",
    )
    # Set once the manufacturer has been emailed that the hub is full, so the
    # alert fires only once per fill cycle (§5.4.3 manufacturer notifications).
    pickup_notified = models.BooleanField(default=False, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        # Reopening a hub (setting it Active) clears the pickup alert so the
        # next time it fills, the manufacturer is notified again.
        if self.status == self.Status.ACTIVE:
            self.pickup_notified = False
        super().save(*args, **kwargs)

    @property
    def is_accepting(self):
        """True when the hub can currently take new drop-offs."""
        return self.status == self.Status.ACTIVE
