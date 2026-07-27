"""
dashboard/forms.py — admin-side forms.
"""

from django import forms

from hubs.models import Collection


class CollectionForm(forms.ModelForm):
    """Record a manufacturer buying (collecting) plastic from a hub."""

    class Meta:
        model = Collection
        fields = ("hub", "manufacturer", "weight_kg", "price_per_kg", "notes")
        widgets = {
            "hub": forms.Select(attrs={"class": "form-select"}),
            "manufacturer": forms.Select(attrs={"class": "form-select"}),
            "weight_kg": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0.01"}),
            "price_per_kg": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }
