"""
Seed a starter reward catalogue (report §Abstract: cafeteria vouchers,
recognition certificates). Safe to re-run — uses get_or_create.

Usage:  ./venv/Scripts/python.exe manage.py seed_rewards
"""

from django.core.management.base import BaseCommand

from rewards.models import Reward


class Command(BaseCommand):
    help = "Create sample rewards for demos/testing."

    def handle(self, *args, **options):
        catalogue = [
            ("Cafeteria Voucher (KES 100)", "Redeem for KES 100 off at the campus cafeteria.", 200),
            ("Cafeteria Voucher (KES 250)", "Redeem for KES 250 off at the campus cafeteria.", 450),
            ("ECO-LINK Recognition Certificate", "A certificate recognising your recycling contribution.", 500),
            ("Reusable ECO-LINK Water Bottle", "A branded reusable bottle to cut single-use plastic.", 800),
            ("Tree Planted in Your Name", "We plant a tree on campus in your name.", 1000),
        ]

        created = 0
        for name, description, points in catalogue:
            _, was_created = Reward.objects.get_or_create(
                name=name,
                defaults={"description": description, "points_required": points},
            )
            created += int(was_created)

        self.stdout.write(self.style.SUCCESS(
            f"Seed complete: {Reward.objects.count()} rewards ({created} new)."
        ))
