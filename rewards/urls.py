"""rewards/urls.py — catalogue, redeem, and redemption history routes."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.reward_list, name="reward_list"),
    path("<int:pk>/redeem/", views.redeem_reward, name="redeem_reward"),
    path("mine/", views.my_redemptions, name="my_redemptions"),
]
