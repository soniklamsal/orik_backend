from django.contrib import admin

from .models import Enquiry


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ["name", "business", "email", "phone", "package", "status", "created_at"]
    list_filter = ["status", "package", "created_at"]
    search_fields = ["name", "business", "email", "phone", "message"]
    list_editable = ["status"]
    date_hierarchy = "created_at"
    readonly_fields = ["created_at", "ip_address", "user_agent"]
    list_per_page = 50

    fieldsets = [
        ("Enquiry", {"fields": ["name", "business", "email", "phone", "package", "message"]}),
        ("Handling", {"fields": ["status"]}),
        ("Received", {"fields": ["created_at", "ip_address", "user_agent"], "classes": ["collapse"]}),
    ]

    @admin.action(description="Mark selected enquiries as contacted")
    def mark_contacted(self, request, queryset):
        updated = queryset.update(status=Enquiry.Status.CONTACTED)
        self.message_user(request, f"{updated} enquiry(s) marked as contacted.")

    actions = ["mark_contacted"]

    def has_add_permission(self, request):
        # Enquiries only arrive through the API.
        return False