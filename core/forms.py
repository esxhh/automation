from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import AuditRequest, Inquiry


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254)

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "email")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        user_model = get_user_model()
        if user_model.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ["name", "email", "company", "service", "message"]

    def clean_name(self):
        return self.cleaned_data["name"].strip()

    def clean_message(self):
        message = self.cleaned_data["message"].strip()
        if len(message) < 10:
            raise forms.ValidationError("Please tell us a little more (at least 10 characters).")
        return message


class AuditForm(forms.ModelForm):
    # Accept "example.com" without a scheme.
    website = forms.URLField(max_length=200, assume_scheme="https")

    class Meta:
        model = AuditRequest
        fields = ["business_name", "website", "email"]
