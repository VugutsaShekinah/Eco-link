"""
dropoffs/tests.py — the core business logic of ECO-LINK.

Covers: the points formula, the verification signal (award once, only on
verify), weight validation, and the logging view.

Run with:  ./venv/Scripts/python.exe manage.py test dropoffs
"""

from decimal import Decimal

from django.core import mail
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from hubs.models import Hub, Manufacturer

from .models import DropOff
from .points import calculate_points


class HubCapacityNotificationTests(TestCase):
    """Manufacturer is emailed once when a hub fills up (§5.4.3)."""

    def setUp(self):
        self.user = User.objects.create_user(email="u@example.com", password="x")
        self.mfr = Manufacturer.objects.create(
            name="GreenCycle", email="collect@greencycle.co.ke"
        )
        self.hub = Hub.objects.create(
            name="Gate Hub", location="Main gate",
            capacity_kg=Decimal("5.00"), manufacturer=self.mfr,
        )

    def _verify(self, kg):
        return DropOff.objects.create(
            user=self.user, hub=self.hub, plastic_type="BOTTLES",
            weight_kg=Decimal(kg), status=DropOff.Status.VERIFIED,
        )

    def test_no_email_below_capacity(self):
        self._verify("3.00")
        self.assertEqual(len(mail.outbox), 0)

    def test_email_and_full_status_at_capacity(self):
        self._verify("3.00")
        self._verify("2.00")  # total 5.00 == capacity
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("ready for pickup", mail.outbox[0].subject)
        self.hub.refresh_from_db()
        self.assertEqual(self.hub.status, Hub.Status.FULL)
        self.assertTrue(self.hub.pickup_notified)

    def test_email_sent_only_once(self):
        self._verify("6.00")   # already over capacity -> email
        self._verify("1.00")   # hub already notified -> no second email
        self.assertEqual(len(mail.outbox), 1)

    def test_no_email_without_manufacturer_email(self):
        self.mfr.email = ""
        self.mfr.save()
        self._verify("6.00")
        self.assertEqual(len(mail.outbox), 0)


class PointsFormulaTests(TestCase):
    def test_ten_points_per_kg(self):
        self.assertEqual(calculate_points(Decimal("2.50")), 25)
        self.assertEqual(calculate_points(1), 10)
        self.assertEqual(calculate_points("0.50"), 5)

    def test_truncates_to_whole_points(self):
        # 0.25 kg * 10 = 2.5 -> 2 whole points
        self.assertEqual(calculate_points(Decimal("0.25")), 2)


class DropOffModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="u@example.com", password="x", first_name="U", last_name="One"
        )
        self.hub = Hub.objects.create(
            name="Cafe Hub", location="Cafeteria", capacity_kg=Decimal("100.00")
        )

    def _make(self, **kw):
        defaults = dict(
            user=self.user, hub=self.hub,
            plastic_type=DropOff.PlasticType.BOTTLES, weight_kg=Decimal("2.00"),
        )
        defaults.update(kw)
        return DropOff.objects.create(**defaults)

    def test_new_dropoff_is_pending_and_unpaid(self):
        d = self._make()
        self.assertEqual(d.status, DropOff.Status.PENDING)
        self.assertIsNone(d.verified_at)
        self.user.refresh_from_db()
        self.assertEqual(self.user.eco_points_balance, 0)  # no points until verified

    def test_verifying_awards_points_once(self):
        d = self._make(weight_kg=Decimal("3.00"))  # 30 points
        d.status = DropOff.Status.VERIFIED
        d.save()

        self.user.refresh_from_db()
        d.refresh_from_db()
        self.assertEqual(self.user.eco_points_balance, 30)
        self.assertIsNotNone(d.verified_at)

        # Saving the already-verified record again must NOT double-award.
        d.save()
        self.user.refresh_from_db()
        self.assertEqual(self.user.eco_points_balance, 30)

    def test_multiple_verified_dropoffs_accumulate(self):
        self._make(weight_kg=Decimal("1.00"), status=DropOff.Status.VERIFIED)
        self._make(weight_kg=Decimal("2.50"), status=DropOff.Status.VERIFIED)
        self.user.refresh_from_db()
        self.assertEqual(self.user.eco_points_balance, 10 + 25)

    def test_weight_must_be_positive(self):
        d = DropOff(user=self.user, hub=self.hub,
                    plastic_type=DropOff.PlasticType.BAGS, weight_kg=Decimal("0.00"))
        with self.assertRaises(ValidationError):
            d.full_clean()


class LogDropOffViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="member@example.com", password="GreenPlanet2026",
            first_name="Mem", last_name="Ber",
        )
        self.active_hub = Hub.objects.create(
            name="Active Hub", location="Gate", capacity_kg=Decimal("50.00")
        )
        self.closed_hub = Hub.objects.create(
            name="Closed Hub", location="Old block",
            capacity_kg=Decimal("50.00"), status=Hub.Status.CLOSED,
        )

    def test_requires_login(self):
        response = self.client.get(reverse("log_dropoff"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_logging_creates_pending_dropoff_for_user(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("log_dropoff"),
            {"hub": self.active_hub.pk, "plastic_type": "BOTTLES", "weight_kg": "2.00"},
        )
        self.assertRedirects(response, reverse("dashboard"))
        d = DropOff.objects.get(user=self.user)
        self.assertEqual(d.status, DropOff.Status.PENDING)
        self.assertEqual(d.hub, self.active_hub)

    def test_closed_hub_not_selectable(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("log_dropoff"),
            {"hub": self.closed_hub.pk, "plastic_type": "BAGS", "weight_kg": "1.00"},
        )
        self.assertEqual(response.status_code, 200)  # form re-rendered with error
        self.assertFalse(DropOff.objects.filter(hub=self.closed_hub).exists())
