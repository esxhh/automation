from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse
from unittest.mock import patch

from .models import AuditRequest, Inquiry

AJAX = {"HTTP_X_REQUESTED_WITH": "fetch", "HTTP_ACCEPT": "application/json"}


class HomeTests(TestCase):
    def test_home_renders_default_content(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Personalised AI agents")
        self.assertContains(response, "csrfmiddlewaretoken")
        self.assertContains(response, "NOUSVA")
        self.assertContains(response, "eshanmahey17@gmail.com")
        self.assertContains(response, "WhatsApp")
        self.assertContains(response, "Open the service assistant")
        self.assertContains(response, "data-chat-endpoint")
        self.assertContains(response, "not a real review")
        self.assertContains(response, "NOUSVA notes")
        self.assertContains(response, "brand-butterfly")
        self.assertContains(response, "service-image")

    def test_service_cards_link_to_detail_pages_in_new_tabs(self):
        response = self.client.get(reverse("home"))
        for slug in (
            "personalised-ai-agents",
            "custom-task-automation",
            "ai-engine-optimization",
        ):
            link = f'href="{reverse("service-detail", args=[slug])}" target="_blank" rel="noopener"'
            self.assertContains(response, link)

    def test_service_detail_pages_render(self):
        titles = {
            "personalised-ai-agents": "Personalised AI agents",
            "custom-task-automation": "Custom task automation",
            "ai-engine-optimization": "AI engine optimization",
        }
        for slug, title in titles.items():
            with self.subTest(slug=slug):
                response = self.client.get(reverse("service-detail", args=[slug]))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, title)
                self.assertContains(response, "What this service can do")

    def test_unknown_service_detail_returns_404(self):
        self.assertEqual(self.client.get("/services/not-a-service/").status_code, 404)

    def test_insight_pages_render_and_unknown_slug_is_404(self):
        response = self.client.get(reverse("insight-detail", args=["where-ai-agents-help-most"]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "where a person should stay in the loop")
        self.assertEqual(self.client.get("/insights/not-an-article/").status_code, 404)


class AuthenticationTests(TestCase):
    def test_account_requires_authentication(self):
        response = self.client.get(reverse("account"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('account')}")

    def test_signup_creates_user_and_signs_them_in(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "eshan",
                "email": "eshanmahey17@gmail.com",
                "password1": "NOUSVA-Strong-Password-827!",
                "password2": "NOUSVA-Strong-Password-827!",
            },
        )
        self.assertRedirects(response, reverse("account"))
        self.assertEqual(response.wsgi_request.user.username, "eshan")
        self.assertContains(self.client.get(reverse("account")), "eshanmahey17@gmail.com")

    def test_duplicate_email_is_rejected(self):
        from django.contrib.auth import get_user_model

        get_user_model().objects.create_user(
            username="existing", email="person@example.com", password="safe-password-123"
        )
        response = self.client.post(
            reverse("signup"),
            {
                "username": "newuser",
                "email": "PERSON@example.com",
                "password1": "NOUSVA-Strong-Password-827!",
                "password2": "NOUSVA-Strong-Password-827!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "An account with this email already exists.")

    def test_login_and_post_logout(self):
        from django.contrib.auth import get_user_model

        get_user_model().objects.create_user(
            username="member", email="member@example.com", password="safe-password-123"
        )
        response = self.client.post(
            reverse("login"), {"username": "member", "password": "safe-password-123"}
        )
        self.assertRedirects(response, reverse("account"))
        self.assertEqual(self.client.get(reverse("account")).status_code, 200)
        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)
        self.assertRedirects(self.client.post(reverse("logout")), reverse("home"))
        self.assertRedirects(
            self.client.get(reverse("account")),
            f"{reverse('login')}?next={reverse('account')}",
        )


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


class ChatTests(TestCase):
    def setUp(self):
        cache.clear()
        self.url = reverse("chat")

    @override_settings(CHAT_API_KEY="")
    def test_chat_uses_service_guide_when_api_key_is_missing(self):
        response = self.client.post(
            self.url,
            data='{"messages":[{"role":"user","content":"What does automation do?"}]}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Custom task automation", response.json()["reply"])

    def test_chat_rejects_missing_user_message(self):
        response = self.client.post(
            self.url,
            data='{"messages":[{"role":"assistant","content":"Hello"}]}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_chat_rejects_non_json_body(self):
        response = self.client.post(self.url, data="not json", content_type="application/json")
        self.assertEqual(response.status_code, 400)

    @override_settings(CHAT_API_KEY="test-key")
    @patch("core.views.urlopen")
    def test_chat_uses_configured_ai_provider(self, mock_urlopen):
        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return b'{"choices":[{"message":{"content":"Tell me about your workflow."}}]}'

        mock_urlopen.return_value = FakeResponse()
        response = self.client.post(
            self.url,
            data='{"messages":[{"role":"user","content":"Can you help me?"}]}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["reply"], "Tell me about your workflow.")
        mock_urlopen.assert_called_once()
