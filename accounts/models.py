"""
accounts/models.py — Custom User model for ECO-LINK.

The report (§3.2.3.1, §4.3.1) requires that users register and log in with their
EMAIL (not a username), that each account carries a ROLE (Student / Staff /
Community / Administrator), that it stores a cumulative ECO-POINTS balance, and
that administrators can move an account between Active / Pending / Suspended
(§3.2.3.3). We therefore extend Django's AbstractUser and switch the login field
from `username` to `email`.
"""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """
    Custom manager because we log in by email, not username.

    Django's default UserManager expects a `username`; ours creates users keyed
    on a normalised, unique email address instead.
    """

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("An email address is required.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # hashes with PBKDF2 (report §3.2.2.5)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.Role.ADMIN)
        extra_fields.setdefault("status", User.Status.ACTIVE)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """A single account type for every ECO-LINK participant, distinguished by role."""

    class Role(models.TextChoices):
        STUDENT = "STUDENT", "Student"
        STAFF = "STAFF", "Staff"
        COMMUNITY = "COMMUNITY", "Community Member"
        ADMIN = "ADMIN", "Administrator"

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        PENDING = "PENDING", "Pending"
        SUSPENDED = "SUSPENDED", "Suspended"

    # Remove the username field — we authenticate by email instead.
    username = None

    email = models.EmailField("email address", unique=True)
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT,
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    # Cumulative eco-points from VERIFIED drop-offs (report §3.3.3).
    eco_points_balance = models.PositiveIntegerField(default=0)
    phone_number = models.CharField(max_length=20, blank=True)

    # Tell Django to use email as the login identifier.
    USERNAME_FIELD = "email"
    # Fields prompted for (besides email + password) by `createsuperuser`.
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        full_name = self.get_full_name().strip()
        label = full_name if full_name else self.email
        return f"{label} ({self.get_role_display()})"

    @property
    def is_administrator(self):
        """Convenience check used by role-based access control across the app."""
        return self.role == self.Role.ADMIN
