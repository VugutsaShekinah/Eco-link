"""
hubs/tests.py — unit tests for the Hub and Manufacturer models.

Run with:  ./venv/Scripts/python.exe manage.py test hubs
"""

from decimal import Decimal
from io import StringIO

from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase

from .models import Collection, Hub, Manufacturer


class SeedHubsCommandTests(TestCase):
    def test_seed_creates_hub_and_manufacturer(self):
        call_command("seed_hubs", stdout=StringIO())
        self.assertTrue(Hub.objects.exists())
        self.assertTrue(Manufacturer.objects.exists())

    def test_seed_is_idempotent(self):
        call_command("seed_hubs", stdout=StringIO())
        count = Hub.objects.count()
        call_command("seed_hubs", stdout=StringIO())  # running again must not duplicate
        self.assertEqual(Hub.objects.count(), count)


class ManufacturerModelTests(TestCase):
    def test_str_is_name(self):
        m = Manufacturer.objects.create(name="GreenCycle Ltd")
        self.assertEqual(str(m), "GreenCycle Ltd")

    def test_certified_by_default(self):
        m = Manufacturer.objects.create(name="EcoPlast")
        self.assertTrue(m.is_certified)


class HubModelTests(TestCase):
    def setUp(self):
        self.mfr = Manufacturer.objects.create(name="GreenCycle Ltd")

    def test_str_includes_status(self):
        hub = Hub.objects.create(
            name="Cafeteria Hub", location="Main Cafeteria", capacity_kg=Decimal("100.00")
        )
        self.assertEqual(str(hub), "Cafeteria Hub (Active)")

    def test_defaults_to_active_and_accepting(self):
        hub = Hub.objects.create(
            name="Library Hub", location="Library entrance", capacity_kg=Decimal("50.00")
        )
        self.assertEqual(hub.status, Hub.Status.ACTIVE)
        self.assertTrue(hub.is_accepting)

    def test_non_active_hub_is_not_accepting(self):
        hub = Hub.objects.create(
            name="Closed Hub", location="Old block",
            capacity_kg=Decimal("50.00"), status=Hub.Status.CLOSED,
        )
        self.assertFalse(hub.is_accepting)

    def test_capacity_must_be_positive(self):
        """full_clean() should reject zero/negative capacity (MinValueValidator)."""
        hub = Hub(name="Bad Hub", location="Nowhere", capacity_kg=Decimal("0.00"))
        with self.assertRaises(ValidationError):
            hub.full_clean()

    def test_deleting_manufacturer_keeps_hub(self):
        """on_delete=SET_NULL: removing a recycler must not delete its hubs."""
        hub = Hub.objects.create(
            name="Gate Hub", location="Main gate",
            capacity_kg=Decimal("80.00"), manufacturer=self.mfr,
        )
        self.mfr.delete()
        hub.refresh_from_db()
        self.assertIsNone(hub.manufacturer)
        self.assertTrue(Hub.objects.filter(pk=hub.pk).exists())


class CollectionAndLoadTests(TestCase):
    def setUp(self):
        from accounts.models import User
        from dropoffs.models import DropOff

        self.User = User
        self.DropOff = DropOff
        self.mfr = Manufacturer.objects.create(
            name="PolyAfric", email="buy@poly.co.ke", price_per_kg=Decimal("30.00")
        )
        self.hub = Hub.objects.create(
            name="Gate", location="Main gate",
            capacity_kg=Decimal("100.00"), manufacturer=self.mfr,
        )
        self.user = User.objects.create_user(email="u@example.com", password="x")

    def _verify(self, kg):
        return self.DropOff.objects.create(
            user=self.user, hub=self.hub, plastic_type="BOTTLES",
            weight_kg=Decimal(kg), status=self.DropOff.Status.VERIFIED,
        )

    def test_collection_amount_is_weight_times_price(self):
        c = Collection.objects.create(
            hub=self.hub, manufacturer=self.mfr,
            weight_kg=Decimal("10.00"), price_per_kg=Decimal("30.00"),
        )
        self.assertEqual(c.amount, Decimal("300.00"))

    def test_hub_current_load_is_verified_minus_collected(self):
        self._verify("20.00")
        self._verify("10.00")
        self.assertEqual(self.hub.verified_kg, Decimal("30.00"))
        self.assertEqual(self.hub.current_load_kg, Decimal("30.00"))

        Collection.objects.create(
            hub=self.hub, manufacturer=self.mfr,
            weight_kg=Decimal("25.00"), price_per_kg=Decimal("30.00"),
        )
        self.assertEqual(self.hub.collected_kg, Decimal("25.00"))
        self.assertEqual(self.hub.current_load_kg, Decimal("5.00"))  # 30 - 25
