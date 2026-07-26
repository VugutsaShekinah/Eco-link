"""
dropoffs/test_integration.py — full end-to-end journey (report §4.5.2).

Exercises every module together as one workflow, the way a real user and admin
would, checking the database state at each step:

    register -> log a drop-off (Pending) -> admin verifies (points awarded)
    -> dashboard + leaderboard reflect it -> redeem a reward (points deducted)

Run with:  ./venv/Scripts/python.exe manage.py test dropoffs.test_integration
"""

from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from dropoffs.models import DropOff
from hubs.models import Hub
from rewards.models import Redemption, Reward


class FullJourneyTests(TestCase):
    def setUp(self):
        # A hub to drop off at, an admin to verify, and a reward to redeem.
        self.hub = Hub.objects.create(
            name="Cafeteria Hub", location="Main Cafeteria", capacity_kg=Decimal("100.00")
        )
        self.admin = User.objects.create_user(
            email="admin@ecolink.co.ke", password="adminpass",
            first_name="Ad", last_name="Min", role=User.Role.ADMIN,
        )
        self.reward = Reward.objects.create(name="Cafeteria Voucher", points_required=30)

    def test_register_log_verify_redeem_journey(self):
        student = self.client  # this Client is our student's browser session

        # 1. Register (auto-logs in) --------------------------------------
        resp = student.post(reverse("register"), {
            "first_name": "Amina", "last_name": "Otieno",
            "email": "amina@example.com", "role": "STUDENT",
            "password1": "GreenPlanet2026", "password2": "GreenPlanet2026",
        })
        self.assertRedirects(resp, reverse("dashboard"))
        user = User.objects.get(email="amina@example.com")

        # 2. Log a 5kg drop-off -> Pending, no points yet -----------------
        resp = student.post(reverse("log_dropoff"), {
            "hub": self.hub.pk, "plastic_type": "BOTTLES", "weight_kg": "5.00",
        })
        self.assertRedirects(resp, reverse("dashboard"))
        dropoff = DropOff.objects.get(user=user)
        self.assertEqual(dropoff.status, DropOff.Status.PENDING)
        user.refresh_from_db()
        self.assertEqual(user.eco_points_balance, 0)

        # 3. Admin verifies it -> 50 points awarded -----------------------
        admin_client = self.client_class()
        admin_client.force_login(self.admin)
        resp = admin_client.post(reverse("verify_dropoff", args=[dropoff.pk]))
        self.assertRedirects(resp, reverse("admin_dashboard"))

        dropoff.refresh_from_db()
        user.refresh_from_db()
        self.assertEqual(dropoff.status, DropOff.Status.VERIFIED)
        self.assertIsNotNone(dropoff.verified_at)
        self.assertEqual(user.eco_points_balance, 50)

        # 4. Student's dashboard + leaderboard reflect the new balance ----
        dash = student.get(reverse("dashboard"))
        self.assertEqual(dash.context["my_rank"], 1)

        board = student.get(reverse("leaderboard"))
        self.assertEqual(board.context["my_rank"], 1)
        self.assertIn(user, list(board.context["rankings"]))
        self.assertEqual(board.context["total_kg"], Decimal("5.00"))

        # 5. Redeem a 30-point reward -> balance 20, recorded -------------
        resp = student.post(reverse("redeem_reward", args=[self.reward.pk]))
        self.assertRedirects(resp, reverse("reward_list"))

        user.refresh_from_db()
        self.assertEqual(user.eco_points_balance, 20)
        self.assertEqual(Redemption.objects.filter(user=user).count(), 1)

        # 6. History pages show the records --------------------------------
        self.assertContains(student.get(reverse("my_dropoffs")), "Cafeteria Hub")
        self.assertContains(student.get(reverse("my_redemptions")), "Cafeteria Voucher")

    def test_cannot_redeem_beyond_balance_in_journey(self):
        """A registered user with too few points cannot redeem."""
        student = self.client
        student.post(reverse("register"), {
            "first_name": "Bob", "last_name": "Poor",
            "email": "bob@example.com", "role": "STUDENT",
            "password1": "GreenPlanet2026", "password2": "GreenPlanet2026",
        })
        pricey = Reward.objects.create(name="Water Bottle", points_required=800)

        student.post(reverse("redeem_reward", args=[pricey.pk]))  # balance is 0
        self.assertEqual(Redemption.objects.count(), 0)
        User.objects.get(email="bob@example.com").refresh_from_db()
