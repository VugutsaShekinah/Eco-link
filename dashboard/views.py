"""
dashboard/views.py — the administrator dashboard (§3.2.3.3, §4.3.4).

A dedicated staff interface (separate from Django's /admin/) showing live,
aggregated statistics and the tools admins need most: verifying pending
drop-offs and changing user account status. Every view is gated by the
admin_required decorator, so non-admins are redirected even if they type the URL.

All figures are computed live with ORM aggregates rather than stored counters,
so they are always current (report §4.3.4).
"""

from django.contrib import messages
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.decorators import admin_required
from accounts.models import User
from dropoffs.models import DropOff
from hubs.models import Hub
from rewards.models import Redemption


def _stats():
    """Compute the headline numbers shown on the dashboard (all live)."""
    verified = DropOff.objects.filter(status=DropOff.Status.VERIFIED)

    kg_collected = verified.aggregate(t=Sum("weight_kg"))["t"] or 0
    balance_total = User.objects.aggregate(t=Sum("eco_points_balance"))["t"] or 0
    spent_total = Redemption.objects.aggregate(t=Sum("points_spent"))["t"] or 0

    return {
        "total_users": User.objects.count(),
        "total_dropoffs": DropOff.objects.count(),
        "pending_count": DropOff.objects.filter(status=DropOff.Status.PENDING).count(),
        "kg_collected": kg_collected,
        # Gross points ever awarded = points still held + points already spent.
        "points_awarded": balance_total + spent_total,
        "total_redemptions": Redemption.objects.count(),
        "total_hubs": Hub.objects.count(),
        "active_hubs": Hub.objects.filter(status=Hub.Status.ACTIVE).count(),
    }


@admin_required
def admin_dashboard(request):
    """Stats overview + the queue of drop-offs awaiting verification."""
    context = _stats()
    context["pending_dropoffs"] = (
        DropOff.objects.filter(status=DropOff.Status.PENDING)
        .select_related("user", "hub")[:15]
    )
    return render(request, "dashboard/admin_dashboard.html", context)


@admin_required
@require_POST
def verify_dropoff(request, pk):
    """Verify one pending drop-off — the signal awards the points."""
    dropoff = get_object_or_404(DropOff, pk=pk)
    if dropoff.status == DropOff.Status.VERIFIED:
        messages.info(request, "That drop-off is already verified.")
    else:
        dropoff.status = DropOff.Status.VERIFIED
        dropoff.save()  # triggers the post_save signal -> awards eco-points
        messages.success(
            request,
            f"Verified {dropoff.weight_kg}kg from {dropoff.user.email}. "
            f"{dropoff.calculate_points()} eco-points awarded.",
        )
    return redirect("admin_dashboard")


@admin_required
def manage_users(request):
    """List users with their status, drop-off count, and balance."""
    users = (
        User.objects.annotate(dropoff_count=Count("dropoffs"))
        .order_by("-date_joined")
    )
    return render(
        request,
        "dashboard/manage_users.html",
        {"users": users, "status_choices": User.Status.choices},
    )


@admin_required
@require_POST
def set_user_status(request, pk):
    """Change a user's account status (Active / Pending / Suspended)."""
    target = get_object_or_404(User, pk=pk)
    new_status = request.POST.get("status")

    valid = dict(User.Status.choices)
    if new_status not in valid:
        messages.error(request, "Invalid status.")
    elif target.is_administrator:
        # Don't let admins be suspended/altered through this screen.
        messages.error(request, "Administrator accounts cannot be changed here.")
    else:
        target.status = new_status
        target.save(update_fields=["status"])
        messages.success(request, f"{target.email} is now {valid[new_status]}.")
    return redirect("manage_users")
