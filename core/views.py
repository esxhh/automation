import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.mail import send_mail
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import AuditForm, InquiryForm
from .models import Faq, Service

# Shown until you add your own in the admin (Services / FAQs).
DEFAULT_SERVICES = [
    {
        "title": "Personalised AI agents",
        "slug": "personalised-ai-agents",
        "description": (
            "Agents shaped around your processes, tools and tone of voice. They handle support "
            "questions, lead follow-up, scheduling and reporting, and hand over to you when "
            "judgement is needed."
        ),
        "icon": "agent",
    },
    {
        "title": "Custom task automation",
        "slug": "custom-task-automation",
        "description": (
            "We connect the apps you already use and remove the manual steps between them: data "
            "entry, invoicing, onboarding, approvals and weekly reports."
        ),
        "icon": "automation",
    },
    {
        "title": "AI engine optimization",
        "slug": "ai-engine-optimization",
        "description": (
            "Customers now ask ChatGPT, Claude, Gemini and Perplexity who to trust. We help AI "
            "systems understand, cite and recommend your business."
        ),
        "icon": "aeo",
    },
]

SERVICE_SLUGS = {
    "agent": "personalised-ai-agents",
    "automation": "custom-task-automation",
    "aeo": "ai-engine-optimization",
}

SERVICE_DETAILS = {
    "personalised-ai-agents": {
        "title": "Personalised AI agents",
        "eyebrow": "AI agents",
        "intro": (
            "A practical AI teammate shaped around your business, your tools, and the way your "
            "team already works."
        ),
        "overview": (
            "An AI agent can understand requests, find relevant information, and complete "
            "well-defined tasks across your support and operations workflows. We tailor its "
            "knowledge, tone, permissions, and escalation rules to your needs, with people "
            "remaining in control of important decisions."
        ),
        "outcomes": [
            "Respond to common customer questions using approved business information.",
            "Qualify and route incoming leads, then prepare useful follow-up.",
            "Help with scheduling, internal knowledge lookup, and routine reporting.",
            "Escalate unusual, sensitive, or low-confidence requests to your team.",
        ],
        "examples": [
            "Customer support assistant for FAQs, order questions, and handoffs.",
            "Lead assistant that captures requirements and prepares a team follow-up.",
            "Internal assistant that helps staff find procedures and company knowledge.",
        ],
        "process": [
            "Choose one useful workflow and agree what success looks like.",
            "Connect approved knowledge and tools, then define permissions and escalation rules.",
            "Test real scenarios with your team before a controlled launch.",
            "Review results and refine the agent as your business changes.",
        ],
        "fit": "Teams handling repeated questions or structured work who want faster responses without giving up human oversight.",
    },
    "custom-task-automation": {
        "title": "Custom task automation",
        "eyebrow": "Workflow automation",
        "intro": (
            "Connect the software you already use and remove repetitive handoffs from everyday "
            "work."
        ),
        "overview": (
            "We map the steps between your apps, identify where manual copying or chasing slows "
            "the team down, and build an automation around the process. The workflow can include "
            "checks, notifications, approvals, and a clear route for exceptions."
        ),
        "outcomes": [
            "Move information between connected tools without repeated data entry.",
            "Trigger reminders and updates when a task reaches the right stage.",
            "Keep approval steps visible and send unusual cases to a person.",
            "Reduce missed handoffs while retaining a record of what happened.",
        ],
        "examples": [
            "Create an invoice draft when a project or order reaches an agreed status.",
            "Collect onboarding details and notify the people responsible for each step.",
            "Prepare recurring reports from information already held in your business tools.",
        ],
        "process": [
            "Document the current workflow and the tools involved.",
            "Agree on triggers, validation rules, approvals, and exception handling.",
            "Build and test with sample cases, including failure scenarios.",
            "Launch with monitoring and adjust the workflow using team feedback.",
        ],
        "fit": "Businesses with repeatable processes spanning multiple apps, spreadsheets, or team handoffs.",
    },
    "ai-engine-optimization": {
        "title": "AI engine optimization",
        "eyebrow": "AI visibility",
        "intro": (
            "Make it easier for AI assistants to understand what your business does and when it "
            "is relevant to recommend."
        ),
        "overview": (
            "People increasingly ask AI assistants for recommendations and explanations. We "
            "review how your business is represented online, find gaps or inconsistencies, and "
            "help structure accurate information so it is easier to interpret and cite. No one "
            "can guarantee a particular ranking or mention, but clearer, trustworthy information "
            "gives systems a better foundation."
        ),
        "outcomes": [
            "Understand how your business currently appears in selected AI assistants.",
            "Clarify service descriptions, facts, and answers across important pages.",
            "Improve structured content and the consistency of trusted business profiles.",
            "Track changes over time and identify the next useful improvements.",
        ],
        "examples": [
            "Baseline checks for how assistants answer questions in your category.",
            "A clearer service and FAQ structure based on real customer questions.",
            "An action plan for correcting inconsistent information across key sources.",
        ],
        "process": [
            "Review your website, business profiles, and current AI visibility.",
            "Prioritize the information gaps that matter most to your customers.",
            "Improve content clarity, structure, and consistency across selected sources.",
            "Recheck visibility and keep refining as your business and the tools evolve.",
        ],
        "fit": "Organizations that want accurate, discoverable information wherever customers research and compare providers.",
    },
}

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
    for service in services:
        if not isinstance(service, dict):
            service.slug = SERVICE_SLUGS.get(service.icon, "personalised-ai-agents")
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
            "chat_enabled": bool(settings.CHAT_API_KEY),
        },
    )


def service_detail(request, slug):
    service = SERVICE_DETAILS.get(slug)
    if service is None:
        raise Http404("Service not found")
    return render(
        request,
        "core/service_detail.html",
        {
            "service": service,
            "brand": settings.SITE_NAME,
            "chat_enabled": bool(settings.CHAT_API_KEY),
        },
    )


def _client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def _is_throttled(request, scope, limit=None):
    """Very small per-IP rate limit using Django's cache."""
    key = f"form-rate:{scope}:{_client_ip(request)}"
    if cache.add(key, 1, 60):
        return False
    try:
        count = cache.incr(key)
    except ValueError:
        cache.set(key, 1, 60)
        return False
    return count > (limit or settings.FORM_RATE_LIMIT)


def _assistant_fallback(message):
    text = message.lower()
    if any(word in text for word in ("price", "pricing", "cost", "quote", "charge")):
        return (
            "Pricing depends on the workflow, tools, and level of support involved. Share what "
            "you want to improve in the consultation form and the team can suggest a suitable scope."
        )
    if any(word in text for word in ("agent", "support", "lead", "assistant", "customer")):
        return (
            "Personalised AI agents can answer common questions, qualify leads, help with "
            "scheduling, or find internal information, with clear handoff rules for your team. "
            "See the AI agents service page or tell us which workflow you have in mind."
        )
    if any(word in text for word in ("automation", "invoice", "workflow", "integrat", "apps")):
        return (
            "Custom task automation connects the tools you already use to reduce manual entry "
            "and handoffs. We first map your current process, then agree on triggers, approvals, "
            "and exception handling."
        )
    if any(word in text for word in ("visibility", "optimization", "optimisation", "recommend", "search", "chatgpt")):
        return (
            "AI engine optimization helps make your business information clearer and easier for "
            "AI assistants to interpret and cite. It can include a visibility review, content "
            "structure improvements, and ongoing checks; specific recommendations cannot be guaranteed."
        )
    if any(word in text for word in ("human", "person", "contact", "talk", "consult", "email")):
        return "You can reach the team using the consultation form on the homepage. Tell them what you are trying to improve and which tools you use."
    return (
        "I can help you compare AI agents, workflow automation, and AI visibility. What task "
        "takes up the most time for your team, or what would you like customers to get help with?"
    )


def _assistant_reply(messages):
    if not settings.CHAT_API_KEY:
        return _assistant_fallback(messages[-1][1])

    system_message = {
        "role": "system",
        "content": (
            "You are the helpful website assistant for a small AI automation agency. Help "
            "prospective customers understand three services: personalised AI agents for "
            "customer support, lead follow-up, scheduling, and internal knowledge; custom task "
            "automation connecting existing apps and workflows; and AI engine optimization to "
            "make accurate business information easier for AI assistants to understand and cite. "
            "Ask one concise follow-up question when needed. Recommend a relevant service, explain "
            "that scope and pricing depend on discovery, and direct visitors to the consultation "
            "form when they want a quote or human help. Never promise guaranteed savings, rankings, "
            "or outcomes. Do not claim to have contacted anyone, changed systems, or taken actions. "
            "Do not request sensitive personal or account information. Keep answers warm, brief, "
            "and practical."
        ),
    }
    payload = json.dumps({
        "model": settings.CHAT_MODEL,
        "messages": [system_message] + [
            {"role": role, "content": content} for role, content in messages
        ],
        "max_tokens": 240,
        "temperature": 0.4,
    }).encode("utf-8")
    request = Request(
        settings.CHAT_API_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {settings.CHAT_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=12) as response:
            result = json.loads(response.read().decode("utf-8"))
        answer = result["choices"][0]["message"]["content"].strip()
        if not answer:
            raise ValueError("The assistant returned an empty response.")
        return answer[:1800]
    except (HTTPError, URLError, TimeoutError, ValueError, KeyError, IndexError, TypeError):
        return (
            "I couldn't reach the assistant just now. You can still explore the service pages or "
            "send the team a message through the consultation form."
        )


@require_POST
def chat(request):
    if _is_throttled(request, "chat", settings.CHAT_RATE_LIMIT):
        return JsonResponse({"reply": "Please wait a moment before sending another message."}, status=429)
    if len(request.body) > 16000:
        return JsonResponse({"reply": "That message is too long. Please shorten it and try again."}, status=413)
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"reply": "I couldn't read that message. Please try again."}, status=400)

    raw_messages = data.get("messages") if isinstance(data, dict) else None
    if not isinstance(raw_messages, list):
        return JsonResponse({"reply": "Please send a message to get started."}, status=400)
    messages = []
    for item in raw_messages[-8:]:
        if not isinstance(item, dict) or item.get("role") not in ("user", "assistant"):
            continue
        content = item.get("content")
        if isinstance(content, str) and content.strip():
            messages.append((item["role"], content.strip()[:1200]))
    if not messages or messages[-1][0] != "user":
        return JsonResponse({"reply": "Please send a message to get started."}, status=400)
    return JsonResponse({"reply": _assistant_reply(messages)})


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
