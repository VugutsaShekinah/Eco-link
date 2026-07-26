"""
dropoffs/signals.py — award eco-points when a drop-off is verified.

Report Appendix 2 + §4.3.3: the moment a DropOff's status becomes VERIFIED, the
owning user's eco_points_balance goes up by the drop-off's points, and the
drop-off is stamped with verified_at. The verified_at guard makes this
idempotent — re-saving an already-verified drop-off never awards points twice.
"""

from django.core.mail import send_mail
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from hubs.models import Hub

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


@receiver(post_save, sender=DropOff)
def notify_manufacturer_if_hub_full(sender, instance, **kwargs):
    """
    When a verified drop-off pushes a hub to (or past) its capacity, email the
    hub's certified manufacturer once to schedule a pickup, and mark the hub Full
    (§5.4.3, "Manufacturer Scheduling and Notifications").
    """
    if instance.status != DropOff.Status.VERIFIED:
        return

    hub = instance.hub
    if hub.pickup_notified or not hub.manufacturer or not hub.manufacturer.email:
        return

    collected = (
        hub.dropoffs.filter(status=DropOff.Status.VERIFIED)
        .aggregate(t=Sum("weight_kg"))["t"] or 0
    )
    if collected >= hub.capacity_kg:
        send_mail(
            subject=f"[ECO-LINK] {hub.name} is ready for pickup",
            message=(
                f"Hi {hub.manufacturer.name},\n\n"
                f"{hub.name} at {hub.location} has reached its capacity of "
                f"{hub.capacity_kg} kg ({collected} kg collected). "
                f"Please schedule a collection.\n\n— ECO-LINK"
            ),
            from_email=None,  # uses DEFAULT_FROM_EMAIL
            recipient_list=[hub.manufacturer.email],
            fail_silently=True,
        )
        hub.status = Hub.Status.FULL
        hub.pickup_notified = True
        hub.save(update_fields=["status", "pickup_notified"])
