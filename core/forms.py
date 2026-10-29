from django import forms

from .models import AuditRequest, Inquiry


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
