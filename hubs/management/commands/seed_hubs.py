"""
Seed a few demo hubs and a certified manufacturer so the app is immediately
usable and demoable. Safe to re-run — it uses get_or_create (no duplicates).

Usage:  ./venv/Scripts/python.exe manage.py seed_hubs
"""

from decimal import Decimal

from django.core.management.base import BaseCommand

from hubs.models import Hub, Manufacturer


class Command(BaseCommand):
    help = "Create sample hubs and a manufacturer for demos/testing."

    def handle(self, *args, **options):
        mfr, _ = Manufacturer.objects.get_or_create(
            name="GreenCycle Recyclers Ltd",
            defaults={
                "email": "collect@greencycle.co.ke",
                "phone_number": "+254700000000",
                "location": "Industrial Area, Nairobi",
                "materials_accepted": "Bottles, Hard plastics, Mixed plastics",
                "price_per_kg": Decimal("25.00"),
            },
        )
        # A second certified recycler (PolyAfric makes fencing posts and boards
        # from recycled plastic) that the university can also sell to.
        Manufacturer.objects.get_or_create(
            name="PolyAfric Recycling",
            defaults={
                "email": "buy@polyafric.co.ke",
                "phone_number": "+254711000000",
                "location": "Athi River, Machakos",
                "materials_accepted": "Hard plastics, Bottles",
                "price_per_kg": Decimal("30.00"),
            },
        )

        # ECO-LINK operates a single collection hub at the Main Gate.
        _, was_created = Hub.objects.get_or_create(
            name="Main Gate Hub",
            defaults={
                "location": "Near the main gate",
                "capacity_kg": Decimal("120.00"),
                "manufacturer": mfr,
            },
        )

        self.stdout.write(self.style.SUCCESS(
            f"Seed complete: {Hub.objects.count()} hub(s) "
            f"({int(was_created)} new), {Manufacturer.objects.count()} manufacturers."
        ))
