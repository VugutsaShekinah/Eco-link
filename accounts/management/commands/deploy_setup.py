"""
deploy_setup.py — idempotent post-deploy setup for hosted environments (Render).

Free hosting tiers often have no interactive shell, so this command runs during
the deploy build to guarantee the app is usable:

  1. seeds the collection hub + manufacturers + rewards (so the drop-off form is
     never empty), and
  2. guarantees a working administrator account you can always log in with.

Everything here is safe to run on every deploy — it never duplicates data.

Admin login:
  * If you set DJANGO_SUPERUSER_EMAIL and DJANGO_SUPERUSER_PASSWORD (host
    dashboard), those are used.
  * Otherwise a DEFAULT admin is created/refreshed so you are never locked out:
        email:    admin@eco-link.co.ke
        password: EcoLink2026!
    (Change this password after logging in.)
"""

import os

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand

DEFAULT_ADMIN_EMAIL = "admin@eco-link.co.ke"
DEFAULT_ADMIN_PASSWORD = "EcoLink2026!"


class Command(BaseCommand):
    help = "Seed baseline data and ensure a working admin account (idempotent)."

    def handle(self, *args, **options):
        # 1. Baseline data so the app works immediately.
        #    Route sub-command output through our own stdout (keeps test output
        #    clean; still visible in the deploy logs).
        call_command("seed_hubs", stdout=self.stdout)
        call_command("seed_rewards", stdout=self.stdout)

        # Optionally load sample participants + drop-offs for a populated demo
        # (set RUN_SEED_DEMO=1 in the environment).
        if os.environ.get("RUN_SEED_DEMO") == "1":
            call_command("seed_demo", stdout=self.stdout)

        # 2. Ensure a working admin account.
        #    Prefer env-var credentials; otherwise fall back to a documented
        #    default so you can always log in without touching the dashboard.
        env_email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        env_password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if env_email and env_password:
            email, password, using_default = env_email, env_password, False
        else:
            email, password, using_default = (
                DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_PASSWORD, True,
            )

        User = get_user_model()
        user = User.objects.filter(email__iexact=email).first()

        if user is None:
            User.objects.create_superuser(
                email=email,
                password=password,
                first_name=os.environ.get("DJANGO_SUPERUSER_FIRST_NAME", "Admin"),
                last_name=os.environ.get("DJANGO_SUPERUSER_LAST_NAME", ""),
            )
            action = "Created"
        else:
            # Make sure it's a full admin and set the password so it always works.
            user.role = User.Role.ADMIN
            user.status = User.Status.ACTIVE
            user.is_staff = True
            user.is_superuser = True
            user.set_password(password)
            user.save()
            action = "Reset"

        note = "  <-- DEFAULT login, change the password after logging in" if using_default else ""
        self.stdout.write(self.style.SUCCESS(
            f"{action} admin login:  {email}  /  {password}{note}"
        ))
