"""
accounts/tests.py — unit tests for registration, login, and access control.

Run with:  ./venv/Scripts/python.exe manage.py test accounts
"""

from django.test import TestCase
from django.urls import reverse

from .models import User


class RegistrationTests(TestCase):
    def test_register_creates_user_and_logs_in(self):
        """A valid Student registration creates the account and redirects to dashboard."""
        response = self.client.post(
            reverse("register"),
            {
                "first_name": "Amina",
                "last_name": "Otieno",
                "email": "amina@example.com",
                "role": "STUDENT",
                "password1": "GreenPlanet2026",
                "password2": "GreenPlanet2026",
            },
        )
        self.assertRedirects(response, reverse("dashboard"))
        user = User.objects.get(email="amina@example.com")
        self.assertEqual(user.role, User.Role.STUDENT)
        self.assertEqual(user.status, User.Status.ACTIVE)
        self.assertEqual(user.eco_points_balance, 0)
        # Password must be hashed, never stored in plain text.
        self.assertNotEqual(user.password, "GreenPlanet2026")
        self.assertTrue(user.check_password("GreenPlanet2026"))

    def test_duplicate_email_rejected(self):
        User.objects.create_user(
            email="dup@example.com", password="x", first_name="A", last_name="B"
        )
        response = self.client.post(
            reverse("register"),
            {
                "first_name": "Copy",
                "last_name": "Cat",
                "email": "dup@example.com",
                "role": "STUDENT",
                "password1": "GreenPlanet2026",
                "password2": "GreenPlanet2026",
            },
        )
        self.assertEqual(response.status_code, 200)  # re-rendered with errors
        self.assertContains(response, "already exists")
        self.assertEqual(User.objects.filter(email="dup@example.com").count(), 1)

    def test_cannot_self_register_as_administrator(self):
        """The public form must reject the Administrator role (§3.2.3.1)."""
        response = self.client.post(
            reverse("register"),
            {
                "first_name": "Sneaky",
                "last_name": "User",
                "email": "sneaky@example.com",
                "role": "ADMIN",
                "password1": "GreenPlanet2026",
                "password2": "GreenPlanet2026",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email="sneaky@example.com").exists())


class UserManagerTests(TestCase):
    def test_create_user_requires_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="x")

    def test_create_user_hashes_password(self):
        u = User.objects.create_user(email="a@example.com", password="secret123")
        self.assertNotEqual(u.password, "secret123")
        self.assertTrue(u.check_password("secret123"))

    def test_create_superuser_is_admin(self):
        su = User.objects.create_superuser(email="su@example.com", password="x")
        self.assertTrue(su.is_staff)
        self.assertTrue(su.is_superuser)
        self.assertEqual(su.role, User.Role.ADMIN)
        self.assertEqual(su.status, User.Status.ACTIVE)
        self.assertTrue(su.is_administrator)

    def test_display_name_prefers_full_name_then_email_localpart(self):
        named = User.objects.create_user(
            email="amina@example.com", password="x",
            first_name="Amina", last_name="Otieno",
        )
        self.assertEqual(named.display_name, "Amina Otieno")

        nameless = User.objects.create_user(email="justme@example.com", password="x")
        self.assertEqual(nameless.display_name, "justme")  # email local-part, not full email

    def test_superuser_must_have_staff_and_superuser_flags(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(email="x@example.com", password="x", is_staff=False)
        with self.assertRaises(ValueError):
            User.objects.create_superuser(email="y@example.com", password="x", is_superuser=False)


class DeploySetupCommandTests(TestCase):
    """The deploy-time setup must seed a usable hub and create the admin."""

    def test_seeds_hub_and_creates_admin_from_env(self):
        import os
        from io import StringIO

        from django.core.management import call_command

        from hubs.models import Hub

        os.environ["DJANGO_SUPERUSER_EMAIL"] = "boss@example.com"
        os.environ["DJANGO_SUPERUSER_PASSWORD"] = "StrongPass123!"
        try:
            call_command("deploy_setup", stdout=StringIO())
        finally:
            os.environ.pop("DJANGO_SUPERUSER_EMAIL", None)
            os.environ.pop("DJANGO_SUPERUSER_PASSWORD", None)

        # A usable, ACTIVE hub exists so the drop-off dropdown is never empty.
        self.assertTrue(Hub.objects.filter(status=Hub.Status.ACTIVE).exists())
        # The admin account was created.
        admin = User.objects.get(email="boss@example.com")
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_administrator)

    def test_creates_default_admin_when_no_env_vars(self):
        from io import StringIO

        from django.core.management import call_command

        # No DJANGO_SUPERUSER_* set -> a documented default admin is created.
        call_command("deploy_setup", stdout=StringIO())

        admin = User.objects.get(email="admin@eco-link.co.ke")
        self.assertTrue(admin.is_administrator)
        self.assertTrue(admin.check_password("EcoLink2026!"))

    def test_resets_existing_account_to_admin_with_new_password(self):
        import os
        from io import StringIO

        from django.core.management import call_command

        # An ordinary member forgot their password / isn't an admin yet.
        User.objects.create_user(
            email="me@example.com", password="oldforgotten", role=User.Role.STUDENT
        )
        os.environ["DJANGO_SUPERUSER_EMAIL"] = "me@example.com"
        os.environ["DJANGO_SUPERUSER_PASSWORD"] = "BrandNewPass123!"
        try:
            call_command("deploy_setup", stdout=StringIO())
        finally:
            os.environ.pop("DJANGO_SUPERUSER_EMAIL", None)
            os.environ.pop("DJANGO_SUPERUSER_PASSWORD", None)

        me = User.objects.get(email="me@example.com")
        self.assertTrue(me.is_administrator)          # promoted
        self.assertTrue(me.check_password("BrandNewPass123!"))  # password reset


class MakeAdminCommandTests(TestCase):
    def test_promotes_existing_user(self):
        from io import StringIO

        from django.core.management import call_command

        user = User.objects.create_user(
            email="p@example.com", password="x", role=User.Role.STUDENT
        )
        call_command("make_admin", "p@example.com", stdout=StringIO())
        user.refresh_from_db()
        self.assertTrue(user.is_administrator)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_errors_for_unknown_email(self):
        from django.core.management import CommandError, call_command

        with self.assertRaises(CommandError):
            call_command("make_admin", "nobody@example.com")


class HomePageTests(TestCase):
    def test_anonymous_sees_landing_page(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Turn plastic waste into rewards")

    def test_authenticated_user_redirected_to_dashboard(self):
        user = User.objects.create_user(
            email="u@example.com", password="x", first_name="U", last_name="One"
        )
        self.client.force_login(user)
        response = self.client.get(reverse("home"))
        self.assertRedirects(response, reverse("dashboard"))


class AuthenticationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="member@example.com",
            password="GreenPlanet2026",
            first_name="Mem",
            last_name="Ber",
            role=User.Role.COMMUNITY,
        )

    def test_login_by_email(self):
        response = self.client.post(
            reverse("login"),
            {"username": "member@example.com", "password": "GreenPlanet2026"},
        )
        self.assertRedirects(response, reverse("dashboard"))

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_logout(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("login"))
