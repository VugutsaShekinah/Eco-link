"""leaderboard/urls.py — community leaderboard route."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.leaderboard, name="leaderboard"),
]
