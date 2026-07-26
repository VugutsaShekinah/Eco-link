"""
URL configuration for the ECO-LINK project.

App-specific routes live in each app's urls.py and are wired in here with
include(). Django's own admin site stays at /admin/.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Authentication + dashboard (home, register, login, logout, dashboard)
    path("", include("accounts.urls")),
    # Drop-off logging and history
    path("dropoffs/", include("dropoffs.urls")),
]
