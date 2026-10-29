from django.contrib import admin

from .models import AuditRequest, Faq, Inquiry, Service


@admin.action(description="Mark selected as handled")
def mark_handled(modeladmin, request, queryset):
    queryset.update(is_handled=True)


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "company", "service", "created_at", "is_handled")
    list_filter = ("is_handled", "service", "created_at")
    search_fields = ("name", "email", "company", "message")
    readonly_fields = ("created_at",)
    actions = [mark_handled]


@admin.register(AuditRequest)
class AuditRequestAdmin(admin.ModelAdmin):
    list_display = ("business_name", "website", "email", "created_at", "is_handled")
    list_filter = ("is_handled", "created_at")
    search_fields = ("business_name", "website", "email")
    readonly_fields = ("created_at",)
    actions = [mark_handled]


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "icon", "order", "is_active")
    list_editable = ("order", "is_active")


@admin.register(Faq)
class FaqAdmin(admin.ModelAdmin):
    list_display = ("question", "order", "is_active")
    list_editable = ("order", "is_active")
