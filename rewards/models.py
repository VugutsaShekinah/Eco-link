"""
rewards/models.py — the reward catalogue and redemption records (§3.2.3.3, §3.3.3).

- Reward     : a catalogue item a user can redeem eco-points for (e.g. a
               cafeteria voucher), with the points it costs.
- Redemption : a record of one user spending points on one reward — the junction
               table capturing the many-to-many relationship between Users and
               Rewards, with the points spent snapshotted at redemption time.
"""

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Reward(models.Model):
    """An item users can redeem their eco-points for."""

    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    points_required = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Eco-points needed to redeem this reward.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Only active rewards appear in the catalogue.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["points_required", "name"]

    def __str__(self):
        return f"{self.name} ({self.points_required} pts)"


class Redemption(models.Model):
    """A single 'user spent points on a reward' transaction."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="redemptions",
    )
    reward = models.ForeignKey(
        Reward,
        on_delete=models.PROTECT,     # keep history even if a reward is retired
        related_name="redemptions",
    )
    # Snapshot of the cost at redemption time, so later price changes don't
    # rewrite history.
    points_spent = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} redeemed {self.reward.name} (-{self.points_spent} pts)"
