"""
accounts/decorators.py — reusable role-based access control (RBAC).

The report requires that students, staff, and community members cannot reach any
administrator-only view, even by typing the URL directly (§3.2.2.5, §4.3.4).
These small decorators enforce that consistently across the codebase.
"""

from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def admin_required(view_func):
    """Allow only authenticated Administrator accounts; redirect everyone else."""

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        if not request.user.is_administrator:
            messages.error(request, "You do not have permission to view that page.")
            return redirect("dashboard")
        return view_func(request, *args, **kwargs)

    return _wrapped
