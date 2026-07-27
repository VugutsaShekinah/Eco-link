"""
Seed realistic demo data (participants + drop-offs + a redemption) so the
dashboards, leaderboard, and history pages look populated for screenshots and
live demos. Safe to re-run — it skips users/drop-offs that already exist.

Usage:  ./venv/Scripts/python.exe manage.py seed_demo
"""

from decimal import Decimal

from django.core.management import call_command
from django.core.management.base import BaseCommand

from accounts.models import User
from dropoffs.models import DropOff
from hubs.models import Hub
from rewards.models import Reward
from rewards.services import redeem

DEMO_USERS = [
    ("amina@example.com", "Amina", "Otieno", User.Role.STUDENT),
    ("brian@example.com", "Brian", "Kamau", User.Role.STUDENT),
    ("carol@example.com", "Carol", "Wanjiku", User.Role.STAFF),
    ("david@example.com", "David", "Mwangi", User.Role.COMMUNITY),
    ("esther@example.com", "Esther", "Njeri", User.Role.STUDENT),
]

# (plastic_type, weight, verify?) drop-offs per user, indexed by position.
DEMO_DROPOFFS = [
    [("BOTTLES", "4.50", True), ("HARD", "2.00", True), ("BAGS", "1.50", False)],
    [("BOTTLES", "3.00", True), ("MIXED", "2.50", True)],
    [("HARD", "5.00", True), ("BOTTLES", "1.00", True), ("MIXED", "0.75", False)],
    [("BAGS", "2.25", True)],
    [("BOTTLES", "6.00", True), ("HARD", "3.50", True), ("MIXED", "1.25", True)],
]


class Command(BaseCommand):
    help = "Create demo participants, drop-offs, and a redemption for screenshots/demos."

    def handle(self, *args, **options):
        # Make sure the hub + rewards exist first.
        call_command("seed_hubs", stdout=self.stdout)
        call_command("seed_rewards", stdout=self.stdout)
        hub = Hub.objects.filter(name="Main Gate Hub").first() or Hub.objects.first()

        created_users = 0
        for i, (email, first, last, role) in enumerate(DEMO_USERS):
            user, was_new = User.objects.get_or_create(
                email=email,
                defaults={"first_name": first, "last_name": last, "role": role},
            )
            if was_new:
                user.set_password("GreenPlanet2026")
                user.save()
                created_users += 1

            # Only add drop-offs if this user has none yet.
            if not user.dropoffs.exists():
                for plastic_type, weight, verify in DEMO_DROPOFFS[i]:
                    DropOff.objects.create(
                        user=user,
                        hub=hub,
                        plastic_type=plastic_type,
                        weight_kg=Decimal(weight),
                        status=DropOff.Status.VERIFIED if verify else DropOff.Status.PENDING,
                    )

        # Give the top earner one redemption so the history page has content.
        esther = User.objects.filter(email="esther@example.com").first()
        cheapest = Reward.objects.filter(is_active=True).order_by("points_required").first()
        if esther and cheapest and not esther.redemptions.exists():
            if esther.eco_points_balance >= cheapest.points_required:
                redeem(esther, cheapest)

        self.stdout.write(self.style.SUCCESS(
            f"Demo seed complete: {User.objects.exclude(role=User.Role.ADMIN).count()} "
            f"participants, {DropOff.objects.count()} drop-offs."
        ))
