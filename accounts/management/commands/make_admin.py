"""
make_admin.py — promote an existing account to Administrator by email.

The person must have registered first (this changes an existing account; it does
not create one). Handy for adding a second admin locally.

Usage:  ./venv/Scripts/python.exe manage.py make_admin someone@example.com

On the live (Render) site there is no shell, so promote a second admin through
the Django admin instead: /admin/ -> Users -> set Role = Administrator and tick
is_staff + is_superuser.
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Promote an existing user to Administrator by email."

    def add_arguments(self, parser):
        parser.add_argument("email", help="Email of the account to promote.")

    def handle(self, *args, **options):
        email = options["email"]
        User = get_user_model()

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise CommandError(
                f"No account found for {email!r}. Ask them to register first."
            )

        user.role = User.Role.ADMIN
        user.status = User.Status.ACTIVE
        user.is_staff = True
        user.is_superuser = True
        user.save(update_fields=["role", "status", "is_staff", "is_superuser"])

        self.stdout.write(self.style.SUCCESS(f"{email} is now an Administrator."))
