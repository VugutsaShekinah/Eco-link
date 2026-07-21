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

from .forms import RegistrationForm


def home(request):
    """Root URL: send logged-in users to their dashboard, others to login."""
    if request.user.is_authenticated:
        return redirect("dashboard")
    return redirect("login")


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
    The user's landing page after login. For now it shows identity and the
    eco-points balance; drop-off history and leaderboard rank are added in later
    milestones once those models exist.
    """
    return render(request, "accounts/dashboard.html", {"user": request.user})
