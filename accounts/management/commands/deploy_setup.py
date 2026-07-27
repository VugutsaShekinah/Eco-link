"""
deploy_setup.py — idempotent post-deploy setup for hosted environments (Render).

Free hosting tiers often have no interactive shell, so this command runs during
the deploy build to guarantee the app is usable:

  1. seeds the collection hub + manufacturers + rewards (so the drop-off form is
     never empty), and
  2. creates an administrator account from environment variables, if provided.

Everything here is safe to run on every deploy — it never duplicates data.

Set these env vars (in the Render dashboard) to get an admin account:
    DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_PASSWORD
    (optional) DJANGO_SUPERUSER_FIRST_NAME, DJANGO_SUPERUSER_LAST_NAME
"""

import os

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Seed baseline data and ensure an admin account exists (idempotent)."

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

        # 2. Admin account from environment variables (if configured).
        #    This is AUTHORITATIVE: the env email + password always work after a
        #    deploy, so a forgotten password can never lock you out — just update
        #    the values in the host dashboard and redeploy.
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if not (email and password):
            self.stdout.write(
                "No DJANGO_SUPERUSER_EMAIL/PASSWORD set - skipping admin setup."
            )
            return

        User = get_user_model()
        user = User.objects.filter(email__iexact=email).first()

        if user is None:
            User.objects.create_superuser(
                email=email,
                password=password,
                first_name=os.environ.get("DJANGO_SUPERUSER_FIRST_NAME", "Admin"),
                last_name=os.environ.get("DJANGO_SUPERUSER_LAST_NAME", ""),
            )
            self.stdout.write(self.style.SUCCESS(f"Created admin account: {email}"))
        else:
            # Ensure it's a full admin and reset the password to match the env.
            user.role = User.Role.ADMIN
            user.status = User.Status.ACTIVE
            user.is_staff = True
            user.is_superuser = True
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(
                f"Updated admin account {email} (password set from environment)."
            ))
