"""
dropoffs/admin.py — admin screens + the verification workflow (§3.2.3.3, §4.3.4).

Administrators verify pending drop-offs here. Verifying saves each record
individually so the post_save signal fires and awards eco-points — a bulk
queryset .update() would bypass signals and must NOT be used for this.
"""

from django.contrib import admin

from .models import DropOff


@admin.register(DropOff)
class DropOffAdmin(admin.ModelAdmin):
    list_display = ("user", "hub", "plastic_type", "weight_kg",
                    "points_preview", "status", "created_at", "verified_at")
    list_filter = ("status", "plastic_type", "hub")
    search_fields = ("user__email", "user__first_name", "user__last_name", "hub__name")
    date_hierarchy = "created_at"
    autocomplete_fields = ("user", "hub")
    readonly_fields = ("created_at", "verified_at")
    actions = ("verify_dropoffs",)

    @admin.display(description="points")
    def points_preview(self, obj):
        return obj.calculate_points()

    @admin.action(description="Verify selected drop-offs (award eco-points)")
    def verify_dropoffs(self, request, queryset):
        verified = 0
        for dropoff in queryset.filter(status=DropOff.Status.PENDING):
            dropoff.status = DropOff.Status.VERIFIED
            dropoff.save()          # triggers the signal -> awards points
            verified += 1
        self.message_user(request, f"{verified} drop-off(s) verified and points awarded.")
