"""dashboard/urls.py — administrator dashboard routes (all admin-only)."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.admin_dashboard, name="admin_dashboard"),
    path("dropoffs/<int:pk>/verify/", views.verify_dropoff, name="verify_dropoff"),
    path("dropoffs/export.csv", views.export_dropoffs_csv, name="export_dropoffs_csv"),
    path("collections/new/", views.record_collection, name="record_collection"),
    path("users/", views.manage_users, name="manage_users"),
    path("users/<int:pk>/status/", views.set_user_status, name="set_user_status"),
    path("users/<int:pk>/promote/", views.promote_user, name="promote_user"),
    path("users/<int:pk>/demote/", views.demote_user, name="demote_user"),
]
