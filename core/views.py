from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import AuditForm, InquiryForm
from .models import Faq, Service

# Shown until you add your own in the admin (Services / FAQs).
DEFAULT_SERVICES = [
    {
        "title": "Personalised AI agents",
        "description": (
            "Agents shaped around your processes, tools and tone of voice. They handle support "
            "questions, lead follow-up, scheduling and reporting, and hand over to you when "
            "judgement is needed."
        ),
        "icon": "agent",
    },
    {
        "title": "Custom task automation",
        "description": (
            "We connect the apps you already use and remove the manual steps between them: data "
            "entry, invoicing, onboarding, approvals and weekly reports."
        ),
        "icon": "automation",
    },
    {
        "title": "AI engine optimization",
        "description": (
            "Customers now ask ChatGPT, Claude, Gemini and Perplexity who to trust. We help AI "
            "systems understand, cite and recommend your business."
        ),
        "icon": "aeo",
    },
]

DEFAULT_FAQS = [
    {
        "question": "How long does it take to launch an agent?",
        "answer": (
            "It depends on the scope. After the discovery call we send a clear plan and timeline "
            "before any building starts."
        ),
    },
    {
        "question": "Do I need technical knowledge?",
        "answer": "No. We explain everything in plain language and handle the technical setup for you.",
    },
    {
        "question": "Will an agent replace my team?",
        "answer": (
            "Agents take over repetitive tasks so your team can focus on work that needs judgement. "
            "You decide what the agent may do on its own and what needs your approval."
        ),
    },
    {
        "question": "Can it work with the tools I already use?",
        "answer": "In most cases yes. We check compatibility with your tools during discovery.",
    },
    {
        "question": "What is AI engine optimization?",
        "answer": (
            "It is the work of making your business easy for AI assistants to understand, cite and "
            "recommend, through clear content, structured data and trusted sources."
        ),
    },
]


def home(request):
    services = list(Service.objects.filter(is_active=True)) or DEFAULT_SERVICES
    faqs = list(Faq.objects.filter(is_active=True)) or DEFAULT_FAQS
    return render(
        request,
        "core/index.html",
        {
            "services": services,
            "faqs": faqs,
            "service_choices": InquiryForm.base_fields["service"].choices,
            "brand": settings.SITE_NAME,
            "contact_email": settings.CONTACT_EMAIL,
            "contact_phone": settings.CONTACT_PHONE,
        },
    )


def _client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def _is_throttled(request, scope):
    """Very small per-IP rate limit using Django's cache."""
    key = f"form-rate:{scope}:{_client_ip(request)}"
    if cache.add(key, 1, 60):
        return False
    try:
        count = cache.incr(key)
    except ValueError:
        cache.set(key, 1, 60)
        return False
    return count > settings.FORM_RATE_LIMIT


def _wants_json(request):
    return (
        request.headers.get("x-requested-with") == "fetch"
        or "application/json" in request.headers.get("accept", "")
    )


def _notify(subject, body):
    if settings.NOTIFY_EMAIL:
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [settings.NOTIFY_EMAIL],
            fail_silently=True,
        )


def _respond(request, ok, message, errors=None, status=200):
    if _wants_json(request):
        payload = {"ok": ok, "message": message}
        if errors:
            payload["errors"] = {field: [str(e) for e in errs] for field, errs in errors.items()}
        return JsonResponse(payload, status=status)
    (messages.success if ok else messages.error)(request, message)
    return redirect("/#contact")


@require_POST
def contact(request):
    if request.POST.get("nickname"):  # honeypot: real visitors never fill this in
        return _respond(request, True, "Thank you! We will be in touch soon.")
    if _is_throttled(request, "contact"):
        return _respond(request, False, "Too many attempts. Please wait a minute and try again.", status=429)

    form = InquiryForm(request.POST)
    if not form.is_valid():
        return _respond(request, False, "Please check the highlighted fields.", form.errors, 400)

    inquiry = form.save()
    _notify(
        f"New enquiry from {inquiry.name}",
        f"Name: {inquiry.name}\nEmail: {inquiry.email}\nCompany: {inquiry.company or '-'}\n"
        f"Interested in: {inquiry.get_service_display()}\n\n{inquiry.message}",
    )
    return _respond(request, True, "Thank you! We will be in touch soon.")


@require_POST
def audit(request):
    if request.POST.get("nickname"):
        return _respond(request, True, "Request received. We will email you your AI visibility check.")
    if _is_throttled(request, "audit"):
        return _respond(request, False, "Too many attempts. Please wait a minute and try again.", status=429)

    form = AuditForm(request.POST)
    if not form.is_valid():
        return _respond(request, False, "Please check the highlighted fields.", form.errors, 400)

    audit_request = form.save()
    _notify(
        f"AI visibility check requested: {audit_request.business_name}",
        f"Business: {audit_request.business_name}\nWebsite: {audit_request.website}\n"
        f"Email: {audit_request.email}",
    )
    return _respond(request, True, "Request received. We will email you your AI visibility check.")
