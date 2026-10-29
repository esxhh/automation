from django.db import models


class Service(models.Model):
    """A service card on the home page. Editable in the admin."""

    ICON_CHOICES = [
        ("agent", "AI agent"),
        ("automation", "Task automation"),
        ("aeo", "AI engine optimization"),
    ]

    title = models.CharField(max_length=80)
    description = models.TextField()
    icon = models.CharField(max_length=20, choices=ICON_CHOICES, default="agent")
    order = models.PositiveSmallIntegerField(default=0, help_text="Lower numbers appear first.")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class Faq(models.Model):
    """A question and answer in the FAQ accordion."""

    question = models.CharField(max_length=200)
    answer = models.TextField()
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question


class Inquiry(models.Model):
    """A message sent through the contact form."""

    SERVICE_CHOICES = [
        ("agents", "Personalised AI agents"),
        ("automation", "Task automation"),
        ("aeo", "AI engine optimization"),
        ("unsure", "Not sure yet"),
    ]

    name = models.CharField(max_length=120)
    email = models.EmailField()
    company = models.CharField(max_length=160, blank=True)
    service = models.CharField(max_length=20, choices=SERVICE_CHOICES, default="unsure")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_handled = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "inquiries"

    def __str__(self):
        return f"{self.name} <{self.email}>"


class AuditRequest(models.Model):
    """A request for a free AI visibility check."""

    business_name = models.CharField(max_length=160)
    website = models.URLField(max_length=200)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_handled = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.business_name} ({self.website})"
