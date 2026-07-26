"""
dropoffs/views.py — log a drop-off and view your own drop-off history.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import DropOffForm
from .points import POINTS_PER_KG


@login_required
def log_dropoff(request):
    """Record a new plastic drop-off for the logged-in user (status: Pending)."""
    if request.method == "POST":
        form = DropOffForm(request.POST)
        if form.is_valid():
            dropoff = form.save(commit=False)
            dropoff.user = request.user          # attribute it to the current user
            dropoff.save()
            messages.success(
                request,
                f"Drop-off logged! You'll earn {dropoff.calculate_points()} "
                f"eco-points once an administrator verifies it.",
            )
            return redirect("dashboard")
    else:
        form = DropOffForm()

    return render(
        request,
        "dropoffs/log_dropoff.html",
        {"form": form, "points_per_kg": POINTS_PER_KG},
    )


@login_required
def my_dropoffs(request):
    """Full history of the current user's drop-offs, newest first."""
    dropoffs = request.user.dropoffs.select_related("hub").all()
    return render(request, "dropoffs/my_dropoffs.html", {"dropoffs": dropoffs})
