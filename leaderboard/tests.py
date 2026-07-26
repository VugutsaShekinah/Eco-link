"""
leaderboard/tests.py — ranking order, self-rank, admin exclusion, impact.

Run with:  ./venv/Scripts/python.exe manage.py test leaderboard
"""

from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from dropoffs.models import DropOff
from hubs.models import Hub

from .ranking import participant_rank


class LeaderboardTests(TestCase):
    def setUp(self):
        # Three participants with different balances + one admin.
        self.alice = self._user("alice@example.com", 300)
        self.bob = self._user("bob@example.com", 500)
        self.carol = self._user("carol@example.com", 100)
        self.admin = self._user("admin@example.com", 999, role=User.Role.ADMIN)

    def _user(self, email, points, role=User.Role.STUDENT):
        u = User.objects.create_user(
            email=email, password="x", first_name=email[:3], last_name="X", role=role
        )
        u.eco_points_balance = points
        u.save(update_fields=["eco_points_balance"])
        return u

    def test_requires_login(self):
        response = self.client.get(reverse("leaderboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_ranked_by_points_descending_and_excludes_admin(self):
        self.client.force_login(self.alice)
        rankings = list(self.client.get(reverse("leaderboard")).context["rankings"])
        self.assertEqual(rankings, [self.bob, self.alice, self.carol])
        self.assertNotIn(self.admin, rankings)  # admin excluded

    def test_participant_rank_helper(self):
        self.assertEqual(participant_rank(self.bob), 1)    # highest
        self.assertEqual(participant_rank(self.alice), 2)
        self.assertEqual(participant_rank(self.carol), 3)
        self.assertIsNone(participant_rank(self.admin))    # admins unranked

    def test_tied_users_share_rank(self):
        tie = self._user("dave@example.com", 500)  # same as bob
        # Two people on 500 points -> both rank 1.
        self.assertEqual(participant_rank(self.bob), 1)
        self.assertEqual(participant_rank(tie), 1)

    def test_my_rank_in_context(self):
        self.client.force_login(self.carol)
        response = self.client.get(reverse("leaderboard"))
        self.assertEqual(response.context["my_rank"], 3)


class ImpactTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="u@example.com", password="x")
        self.hub = Hub.objects.create(
            name="Hub", location="Gate", capacity_kg=Decimal("100.00")
        )
        self.client.force_login(self.user)

    def test_impact_counts_only_verified(self):
        # 4kg verified, 10kg still pending -> impact should reflect only 4kg.
        DropOff.objects.create(
            user=self.user, hub=self.hub, plastic_type="BOTTLES",
            weight_kg=Decimal("4.00"), status=DropOff.Status.VERIFIED,
        )
        DropOff.objects.create(
            user=self.user, hub=self.hub, plastic_type="BAGS",
            weight_kg=Decimal("10.00"),  # pending
        )
        ctx = self.client.get(reverse("leaderboard")).context
        self.assertEqual(ctx["total_kg"], Decimal("4.00"))
        self.assertEqual(ctx["verified_dropoffs"], 1)
        # 4.00 kg / 0.02 kg per item = 200 items
        self.assertEqual(ctx["items_diverted"], 200)
