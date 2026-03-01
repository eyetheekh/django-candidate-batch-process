from django import forms
from django.core.exceptions import ValidationError
from .models import Candidate


class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ["name", "email", "phone_number", "link", "dob"]

        widgets = {
            "dob": forms.DateInput(attrs={"type": "date"}),
        }

    def clean_email(self):
        email = self.cleaned_data["email"]

        if Candidate.objects.filter(email=email).exists():
            raise ValidationError("Candidate with this email already exists.")

        return email
