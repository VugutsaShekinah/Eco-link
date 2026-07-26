"""
dropoffs/signals.py — award eco-points when a drop-off is verified.

Report Appendix 2 + §4.3.3: the moment a DropOff's status becomes VERIFIED, the
owning user's eco_points_balance goes up by the drop-off's points, and the
drop-off is stamped with verified_at. The verified_at guard makes this
idempotent — re-saving an already-verified drop-off never awards points twice.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import DropOff


@receiver(post_save, sender=DropOff)
def award_eco_points(sender, instance, **kwargs):
    # Only act on a verified drop-off that hasn't been credited yet.
    if instance.status == DropOff.Status.VERIFIED and not instance.verified_at:
        awarded = instance.calculate_points()

        user = instance.user
        user.eco_points_balance += awarded
        user.save(update_fields=["eco_points_balance"])

        # Stamp the verification time. This save re-triggers post_save, but the
        # `not instance.verified_at` guard above is now False, so it stops here.
        instance.verified_at = timezone.now()
        instance.save(update_fields=["verified_at"])
