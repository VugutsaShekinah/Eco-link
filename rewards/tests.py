"""
rewards/tests.py — redemption rules.

Run with:  ./venv/Scripts/python.exe manage.py test rewards
"""

from django.test import TestCase
from django.urls import reverse

from accounts.models import User

from .models import Redemption, Reward
from .services import (
    InsufficientPointsError,
    RewardUnavailableError,
    redeem,
)


class RedeemServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="u@example.com", password="x", first_name="U", last_name="One"
        )
        self.reward = Reward.objects.create(name="Voucher", points_required=200)

    def _give(self, points):
        self.user.eco_points_balance = points
        self.user.save(update_fields=["eco_points_balance"])

    def test_successful_redeem_deducts_points_and_records_it(self):
        self._give(500)
        redemption = redeem(self.user, self.reward)

        self.user.refresh_from_db()
        self.assertEqual(self.user.eco_points_balance, 300)  # 500 - 200
        self.assertEqual(redemption.points_spent, 200)
        self.assertEqual(Redemption.objects.count(), 1)

    def test_insufficient_points_blocks_and_does_not_deduct(self):
        self._give(150)
        with self.assertRaises(InsufficientPointsError):
            redeem(self.user, self.reward)

        self.user.refresh_from_db()
        self.assertEqual(self.user.eco_points_balance, 150)  # unchanged
        self.assertEqual(Redemption.objects.count(), 0)

    def test_exact_balance_can_redeem(self):
        self._give(200)
        redeem(self.user, self.reward)
        self.user.refresh_from_db()
        self.assertEqual(self.user.eco_points_balance, 0)

    def test_inactive_reward_cannot_be_redeemed(self):
        self._give(500)
        self.reward.is_active = False
        self.reward.save()
        with self.assertRaises(RewardUnavailableError):
            redeem(self.user, self.reward)
        self.assertEqual(Redemption.objects.count(), 0)


class RedeemViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="member@example.com", password="GreenPlanet2026",
            first_name="Mem", last_name="Ber",
        )
        self.reward = Reward.objects.create(name="Voucher", points_required=200)

    def test_redeem_requires_login(self):
        response = self.client.post(reverse("redeem_reward", args=[self.reward.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_get_does_not_redeem(self):
        """Redeeming must be POST-only (require_POST)."""
        self.client.force_login(self.user)
        self.user.eco_points_balance = 500
        self.user.save()
        response = self.client.get(reverse("redeem_reward", args=[self.reward.pk]))
        self.assertEqual(response.status_code, 405)  # Method Not Allowed
        self.assertEqual(Redemption.objects.count(), 0)

    def test_post_redeems_and_redirects(self):
        self.client.force_login(self.user)
        self.user.eco_points_balance = 500
        self.user.save()
        response = self.client.post(reverse("redeem_reward", args=[self.reward.pk]))
        self.assertRedirects(response, reverse("reward_list"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.eco_points_balance, 300)
