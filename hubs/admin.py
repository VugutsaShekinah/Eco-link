"""
hubs/admin.py — admin screens for collection hubs and recyclers.

Gives administrators the create/update/manage screens the report requires for
hubs and certified manufacturers (§3.2.3.3).
"""

from django.contrib import admin

from .models import Collection, Hub, Manufacturer


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone_number", "location",
                    "price_per_kg", "is_certified", "created_at")
    list_filter = ("is_certified",)
    search_fields = ("name", "email", "location", "materials_accepted")
    ordering = ("name",)


@admin.register(Hub)
class HubAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "capacity_kg", "current_load_kg",
                    "status", "manufacturer", "created_at")
    list_filter = ("status", "manufacturer")
    search_fields = ("name", "location")
    list_editable = ("status",)          # toggle a hub's status straight from the list
    autocomplete_fields = ("manufacturer",)
    ordering = ("name",)


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ("collected_at", "hub", "manufacturer",
                    "weight_kg", "price_per_kg", "amount")
    list_filter = ("manufacturer", "hub")
    search_fields = ("hub__name", "manufacturer__name")
    date_hierarchy = "collected_at"
    autocomplete_fields = ("hub", "manufacturer")
    readonly_fields = ("amount", "collected_at")
