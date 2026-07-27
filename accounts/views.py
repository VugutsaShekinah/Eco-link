"""
accounts/views.py — registration, dashboard, and the home redirect.

Login and logout themselves are handled by Django's built-in LoginView /
LogoutView (wired up in accounts/urls.py) so we don't re-implement session
handling by hand — we only customise the login form and templates.
"""

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ProfileForm, RegistrationForm
from .models import User


def home(request):
    """
    Root URL. Logged-in users go to their dashboard; visitors see a public
    landing page with live programme impact numbers.
    """
    if request.user.is_authenticated:
        return redirect("dashboard")

    from django.db.models import Sum

    from dropoffs.models import DropOff

    verified = DropOff.objects.filter(status=DropOff.Status.VERIFIED)
    context = {
        "total_kg": verified.aggregate(t=Sum("weight_kg"))["t"] or 0,
        "participant_count": User.objects.exclude(role=User.Role.ADMIN).count(),
    }
    return render(request, "accounts/home.html", context)


def register(request):
    """Create a new Student/Staff/Community account, then log the user in."""
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the new user straight in for a smooth first experience.
            login(request, user)
            messages.success(
                request,
                f"Welcome to ECO-LINK, {user.first_name}! Your account is ready.",
            )
            return redirect("dashboard")
    else:
        form = RegistrationForm()

    return render(request, "accounts/register.html", {"form": form})


@login_required
def dashboard(request):
    """
    The user's landing page: identity, eco-points balance, and recent drop-offs.
    (Leaderboard rank is added in Milestone 6.)
    """
    from leaderboard.ranking import participant_rank

    recent_dropoffs = request.user.dropoffs.select_related("hub")[:5]
    pending_count = request.user.dropoffs.filter(status="PENDING").count()
    context = {
        "user": request.user,
        "recent_dropoffs": recent_dropoffs,
        "pending_count": pending_count,
        "my_rank": participant_rank(request.user),
    }
    return render(request, "accounts/dashboard.html", context)


@login_required
def profile(request):
    """View and edit your own profile (name, phone); shows role & access level."""
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("profile")
    else:
        form = ProfileForm(instance=request.user)

    return render(request, "accounts/profile.html", {"form": form, "user": request.user})
