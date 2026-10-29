from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import AuditRequest, Inquiry

AJAX = {"HTTP_X_REQUESTED_WITH": "fetch", "HTTP_ACCEPT": "application/json"}


class HomeTests(TestCase):
    def test_home_renders_default_content(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Personalised AI agents")
        self.assertContains(response, "csrfmiddlewaretoken")


class ContactTests(TestCase):
    def setUp(self):
        cache.clear()
        self.url = reverse("contact")
        self.valid = {
            "name": "Asha",
            "email": "asha@example.com",
            "company": "Asha Foods",
            "service": "agents",
            "message": "We want an agent for customer support.",
        }

    def test_valid_submission_is_saved(self):
        response = self.client.post(self.url, self.valid, **AJAX)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["ok"])
        self.assertEqual(Inquiry.objects.count(), 1)

    def test_invalid_submission_returns_field_errors(self):
        response = self.client.post(self.url, {**self.valid, "email": "nope", "message": "hi"}, **AJAX)
        self.assertEqual(response.status_code, 400)
        errors = response.json()["errors"]
        self.assertIn("email", errors)
        self.assertIn("message", errors)
        self.assertEqual(Inquiry.objects.count(), 0)

    def test_honeypot_is_ignored_silently(self):
        response = self.client.post(self.url, {**self.valid, "nickname": "bot"}, **AJAX)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Inquiry.objects.count(), 0)

    def test_get_is_not_allowed(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)

    @override_settings(FORM_RATE_LIMIT=2)
    def test_rate_limit(self):
        for _ in range(2):
            self.client.post(self.url, self.valid, **AJAX)
        response = self.client.post(self.url, self.valid, **AJAX)
        self.assertEqual(response.status_code, 429)

    def test_non_ajax_post_redirects(self):
        response = self.client.post(self.url, self.valid)
        self.assertEqual(response.status_code, 302)


class AuditTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_audit_accepts_domain_without_scheme(self):
        response = self.client.post(
            reverse("audit"),
            {"business_name": "Asha Foods", "website": "ashafoods.in", "email": "asha@example.com"},
            **AJAX,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(AuditRequest.objects.get().website, "https://ashafoods.in")
