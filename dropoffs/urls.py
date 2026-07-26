"""dropoffs/urls.py — drop-off logging and history routes."""

from django.urls import path

from . import views

urlpatterns = [
    path("log/", views.log_dropoff, name="log_dropoff"),
    path("mine/", views.my_dropoffs, name="my_dropoffs"),
]
