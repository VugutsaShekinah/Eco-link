"""
rewards/admin.py — manage the reward catalogue and view redemptions.

Admins create/manage rewards here (§3.2.3.3). Redemptions are shown read-only:
they are financial-style records created by the redeem flow and must not be
hand-edited (which would let points be spent without a real deduction).
"""

from django.contrib import admin

from .models import Redemption, Reward


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ("name", "points_required", "is_active", "created_at")
    list_filter = ("is_active",)
    list_editable = ("is_active",)
    search_fields = ("name", "description")
    ordering = ("points_required", "name")


@admin.register(Redemption)
class RedemptionAdmin(admin.ModelAdmin):
    list_display = ("user", "reward", "points_spent", "created_at")
    list_filter = ("reward",)
    search_fields = ("user__email", "reward__name")
    date_hierarchy = "created_at"
    readonly_fields = ("user", "reward", "points_spent", "created_at")

    def has_add_permission(self, request):
        # Redemptions are only ever created through the redeem flow.
        return False
