"""
hubs/admin.py — admin screens for collection hubs and recyclers.

Gives administrators the create/update/manage screens the report requires for
hubs and certified manufacturers (§3.2.3.3).
"""

from django.contrib import admin

from .models import Hub, Manufacturer


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone_number", "location",
                    "is_certified", "created_at")
    list_filter = ("is_certified",)
    search_fields = ("name", "email", "location", "materials_accepted")
    ordering = ("name",)


@admin.register(Hub)
class HubAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "capacity_kg", "status",
                    "manufacturer", "created_at")
    list_filter = ("status", "manufacturer")
    search_fields = ("name", "location")
    list_editable = ("status",)          # toggle a hub's status straight from the list
    autocomplete_fields = ("manufacturer",)
    ordering = ("name",)
