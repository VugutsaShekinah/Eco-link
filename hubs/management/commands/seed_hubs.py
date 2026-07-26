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
            },
        )

        sample_hubs = [
            ("Main Cafeteria Hub", "Main Cafeteria entrance", "120.00"),
            ("Library Hub", "Library ground floor", "80.00"),
            ("Hostels Hub", "Student hostels courtyard", "100.00"),
            ("Main Gate Hub", "Near the main gate", "60.00"),
        ]

        created = 0
        for name, location, capacity in sample_hubs:
            _, was_created = Hub.objects.get_or_create(
                name=name,
                defaults={
                    "location": location,
                    "capacity_kg": Decimal(capacity),
                    "manufacturer": mfr,
                },
            )
            created += int(was_created)

        self.stdout.write(self.style.SUCCESS(
            f"Seed complete: {Hub.objects.count()} hubs "
            f"({created} new), 1 manufacturer."
        ))
