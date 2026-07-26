"""
hubs/tests.py — unit tests for the Hub and Manufacturer models.

Run with:  ./venv/Scripts/python.exe manage.py test hubs
"""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import Hub, Manufacturer


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
