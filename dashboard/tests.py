"""
dashboard/tests.py — admin dashboard access control, stats, verify, status.

Run with:  ./venv/Scripts/python.exe manage.py test dashboard
"""

from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from dropoffs.models import DropOff
from hubs.models import Hub


class AccessControlTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@example.com", password="x",
            first_name="Ad", last_name="Min", role=User.Role.ADMIN,
        )
        self.student = User.objects.create_user(
            email="stu@example.com", password="x",
            first_name="Stu", last_name="Dent", role=User.Role.STUDENT,
        )

    def test_anonymous_redirected_to_login(self):
        response = self.client.get(reverse("admin_dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_non_admin_cannot_access(self):
        """A student typing the admin URL is redirected to their dashboard."""
        self.client.force_login(self.student)
        response = self.client.get(reverse("admin_dashboard"))
        self.assertRedirects(response, reverse("dashboard"))

    def test_admin_can_access(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("admin_dashboard"))
        self.assertEqual(response.status_code, 200)


class DashboardActionTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@example.com", password="x",
            first_name="Ad", last_name="Min", role=User.Role.ADMIN,
        )
        self.student = User.objects.create_user(
            email="stu@example.com", password="x",
            first_name="Stu", last_name="Dent", role=User.Role.STUDENT,
        )
        self.hub = Hub.objects.create(
            name="Hub", location="Gate", capacity_kg=Decimal("100.00")
        )
        self.client.force_login(self.admin)

    def test_stats_counts_are_correct(self):
        DropOff.objects.create(
            user=self.student, hub=self.hub,
            plastic_type=DropOff.PlasticType.BOTTLES, weight_kg=Decimal("2.00"),
        )
        response = self.client.get(reverse("admin_dashboard"))
        self.assertEqual(response.context["total_users"], 2)
        self.assertEqual(response.context["total_dropoffs"], 1)
        self.assertEqual(response.context["pending_count"], 1)

    def test_verify_dropoff_awards_points(self):
        dropoff = DropOff.objects.create(
            user=self.student, hub=self.hub,
            plastic_type=DropOff.PlasticType.BOTTLES, weight_kg=Decimal("3.00"),
        )
        response = self.client.post(reverse("verify_dropoff", args=[dropoff.pk]))
        self.assertRedirects(response, reverse("admin_dashboard"))

        dropoff.refresh_from_db()
        self.student.refresh_from_db()
        self.assertEqual(dropoff.status, DropOff.Status.VERIFIED)
        self.assertEqual(self.student.eco_points_balance, 30)

    def test_verify_requires_post(self):
        dropoff = DropOff.objects.create(
            user=self.student, hub=self.hub,
            plastic_type=DropOff.PlasticType.BAGS, weight_kg=Decimal("1.00"),
        )
        response = self.client.get(reverse("verify_dropoff", args=[dropoff.pk]))
        self.assertEqual(response.status_code, 405)

    def test_change_user_status(self):
        response = self.client.post(
            reverse("set_user_status", args=[self.student.pk]),
            {"status": User.Status.SUSPENDED},
        )
        self.assertRedirects(response, reverse("manage_users"))
        self.student.refresh_from_db()
        self.assertEqual(self.student.status, User.Status.SUSPENDED)

    def test_cannot_change_admin_status(self):
        other_admin = User.objects.create_user(
            email="a2@example.com", password="x", role=User.Role.ADMIN,
        )
        self.client.post(
            reverse("set_user_status", args=[other_admin.pk]),
            {"status": User.Status.SUSPENDED},
        )
        other_admin.refresh_from_db()
        self.assertEqual(other_admin.status, User.Status.ACTIVE)  # unchanged


class RecordCollectionTests(TestCase):
    def setUp(self):
        from hubs.models import Collection, Manufacturer

        self.Collection = Collection
        self.admin = User.objects.create_user(
            email="admin@example.com", password="x", role=User.Role.ADMIN,
        )
        self.student = User.objects.create_user(
            email="stu@example.com", password="x", role=User.Role.STUDENT,
        )
        self.mfr = Manufacturer.objects.create(
            name="PolyAfric", price_per_kg=Decimal("30.00")
        )
        self.hub = Hub.objects.create(
            name="Gate Hub", location="Main", capacity_kg=Decimal("100.00"),
            manufacturer=self.mfr, status=Hub.Status.FULL,
        )

    def test_non_admin_blocked(self):
        self.client.force_login(self.student)
        resp = self.client.get(reverse("record_collection"))
        self.assertRedirects(resp, reverse("dashboard"))

    def test_admin_sees_form(self):
        self.client.force_login(self.admin)
        resp = self.client.get(reverse("record_collection") + f"?hub={self.hub.pk}")
        self.assertEqual(resp.status_code, 200)

    def test_recording_sale_creates_collection_and_reopens_hub(self):
        self.client.force_login(self.admin)
        resp = self.client.post(reverse("record_collection"), {
            "hub": self.hub.pk, "manufacturer": self.mfr.pk,
            "weight_kg": "40.00", "price_per_kg": "30.00", "notes": "",
        })
        self.assertRedirects(resp, reverse("admin_dashboard"))

        collection = self.Collection.objects.get()
        self.assertEqual(collection.amount, Decimal("1200.00"))  # 40 * 30
        self.hub.refresh_from_db()
        self.assertEqual(self.hub.status, Hub.Status.ACTIVE)  # emptied/reopened
        self.assertFalse(self.hub.pickup_notified)


class CsvExportTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@example.com", password="x", role=User.Role.ADMIN,
        )
        self.student = User.objects.create_user(
            email="stu@example.com", password="x", role=User.Role.STUDENT,
        )
        self.hub = Hub.objects.create(
            name="Gate Hub", location="Main", capacity_kg=Decimal("100.00")
        )
        DropOff.objects.create(
            user=self.student, hub=self.hub,
            plastic_type="BOTTLES", weight_kg=Decimal("2.00"),
        )

    def test_admin_downloads_csv(self):
        self.client.force_login(self.admin)
        resp = self.client.get(reverse("export_dropoffs_csv"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "text/csv")
        self.assertIn("attachment", resp["Content-Disposition"])
        content = resp.content.decode()
        self.assertIn("Weight (kg)", content)      # header row
        self.assertIn("stu@example.com", content)  # data row

    def test_non_admin_blocked(self):
        self.client.force_login(self.student)
        resp = self.client.get(reverse("export_dropoffs_csv"))
        self.assertRedirects(resp, reverse("dashboard"))
