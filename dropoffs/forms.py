"""
dropoffs/forms.py — the drop-off logging form (§3.2.3.2, §4.3.3).

The user picks a hub, a plastic type, and enters a weight. Only ACTIVE hubs are
offered, since a closed/full hub can't accept new deposits. Weight validation is
inherited from the model field (MinValueValidator), enforced via the ModelForm.
"""

from django import forms

from hubs.models import Hub

from .models import DropOff


class DropOffForm(forms.ModelForm):
    class Meta:
        model = DropOff
        fields = ("hub", "plastic_type", "weight_kg")
        widgets = {
            "hub": forms.Select(attrs={"class": "form-select"}),
            "plastic_type": forms.Select(attrs={"class": "form-select"}),
            "weight_kg": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0.01",
                    "placeholder": "e.g. 2.50",
                    # id used by the live points-preview script
                    "id": "id_weight_kg",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only hubs currently accepting deposits should be selectable.
        self.fields["hub"].queryset = Hub.objects.filter(status=Hub.Status.ACTIVE)
        self.fields["hub"].empty_label = "Choose a collection hub…"
