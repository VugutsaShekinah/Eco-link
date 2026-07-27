"""
accounts/forms.py — registration and login forms for ECO-LINK.

Report basis:
- Registration collects name, email, password and a ROLE chosen from
  Student / Staff / Community tabs (§4.3.1, Figure 8). Administrator is NOT a
  public sign-up option (§3.2.3.1) — admins are created by other admins.
- Login is by EMAIL + password (§4.3.1).
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import User


class ProfileForm(forms.ModelForm):
    """Let a logged-in user edit their own name and phone number."""

    class Meta:
        model = User
        fields = ("first_name", "last_name", "phone_number")
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. +254700000000"}
            ),
        }


# The three roles a member of the public may self-register as.
PUBLIC_ROLE_CHOICES = [
    (User.Role.STUDENT, "Student"),
    (User.Role.STAFF, "Staff"),
    (User.Role.COMMUNITY, "Community Member"),
]


class RegistrationForm(UserCreationForm):
    """
    Sign-up form. Extends Django's UserCreationForm (which already handles the
    two password fields, password confirmation, and strength validation) and
    adds ECO-LINK's name, email, and role fields.
    """

    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "First name"}),
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Last name"}),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "you@example.com"}),
    )
    # Set by the Student/Staff/Community tabs on the registration page (JS writes
    # into this hidden field). Defaults to Student and is restricted to the three
    # public roles, so nobody can register as an Administrator.
    role = forms.ChoiceField(
        choices=PUBLIC_ROLE_CHOICES,
        initial=User.Role.STUDENT,
        widget=forms.HiddenInput(),
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "role")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Style the inherited password fields to match Bootstrap.
        self.fields["password1"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Password"}
        )
        self.fields["password2"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Confirm password"}
        )

    def clean_email(self):
        """Reject duplicate emails with a friendly message (§3.2.3.1)."""
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email


class EmailAuthenticationForm(AuthenticationForm):
    """
    Login form. Django's AuthenticationForm labels its identifier field
    'username'; because our USERNAME_FIELD is 'email', we relabel it and use an
    email input so the page reads correctly.
    """

    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "you@example.com", "autofocus": True}
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Password"}
        )
