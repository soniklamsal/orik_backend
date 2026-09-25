from django.contrib import admin

from .models import (
    DigitalExperiencesSection,
    IndustriesSection,
    Template,
    FaqItem,
    HeroBadge,
    HeroSection,
    Industry,
    Package,
    Problem,
    ProcessStep,
    Project,
    SiteSettings,
    SocialLink,
    Stat,
    TeamMember,
    Testimonial,
    YourIdeaSection,
)


class OrderedAdmin(admin.ModelAdmin):
    """Shared behaviour: reorder and publish straight from the list page."""

    display_columns = []
    list_editable = ["order", "is_published"]
    list_filter = ["is_published"]
    list_per_page = 50

    def __init_subclass__(cls, **kwargs):
        # Set at class-creation time so Django's admin checks can see it.
        super().__init_subclass__(**kwargs)
        cls.list_display = [*cls.display_columns, "order", "is_published"]


class HeroBadgeInline(admin.TabularInline):
    """Edited inside the hero, since a badge has no meaning on its own."""

    model = HeroBadge
    extra = 0
    fields = ["label", "icon", "order", "is_published"]
    ordering = ["order", "id"]


@admin.register(HeroSection)
class HeroSectionAdmin(admin.ModelAdmin):
    list_display = ["heading", "updated_at"]
    inlines = [HeroBadgeInline]
    fieldsets = [
        ("Headline", {"fields": ["heading", "subheading"]}),
        (
            "Qualities card",
            {"fields": ["qualities_label", "qualities"], "description": "The small card under the paragraph."},
        ),
        (
            "Showcase image",
            {"fields": ["image", "image_alt"], "description": "Leave blank to keep the built-in image."},
        ),
    ]

    def has_add_permission(self, request):
        # Singleton: one row, edited in place.
        return not HeroSection.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


class ProblemInline(admin.StackedInline):
    """The three cards, edited inside the section they belong to."""

    model = Problem
    extra = 0
    fields = ["title", "description", "order", "is_published"]
    ordering = ["order", "id"]


@admin.register(YourIdeaSection)
class YourIdeaAdmin(admin.ModelAdmin):
    list_display = ["__str__", "updated_at"]
    inlines = [ProblemInline]
    fieldsets = [
        ("Heading", {"fields": ["heading"], "description": "Press Enter where you want the line to break."}),
        ("Closing line", {"fields": ["closing_text"]}),
        ("Call to action", {"fields": ["cta_label", "cta_href"]}),
    ]

    def has_add_permission(self, request):
        return not YourIdeaSection.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


class StatInline(admin.TabularInline):
    """The counting figures, edited inside their band."""

    model = Stat
    extra = 0
    fields = ["value", "label", "order", "is_published"]
    ordering = ["order", "id"]


@admin.register(DigitalExperiencesSection)
class DigitalExperiencesAdmin(admin.ModelAdmin):
    list_display = ["__str__", "updated_at"]
    inlines = [StatInline]
    fieldsets = [
        ("Heading", {"fields": ["heading"], "description": "Press Enter where you want the line to break."}),
        ("Text link", {"fields": ["link_label", "link_href"]}),
    ]

    def has_add_permission(self, request):
        return not DigitalExperiencesSection.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "phone", "updated_at"]
    fieldsets = [
        ("Identity", {"fields": ["name", "description"]}),
        ("Contact details", {"fields": ["email", "phone", "location"], "description": "Blank fields stay hidden on the site."}),
    ]

    def has_add_permission(self, request):
        # Singleton: one row, edited in place.
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SocialLink)
class SocialLinkAdmin(OrderedAdmin):
    display_columns = ["label", "platform", "href"]


# Stat has no sidebar entry of its own: figures are edited inside
# "Digital experiences" via StatInline.


# Problem has no sidebar entry of its own: the cards are edited inside
# "Your idea" via ProblemInline, so there is one place to change that section.


@admin.register(Template)
class TemplateAdmin(OrderedAdmin):
    """The demo-site library. Editing one updates every preview using it."""

    display_columns = ["name", "domain", "used_by"]
    search_fields = ["name", "domain", "headline", "subline"]
    prepopulated_fields = {"key": ["name"]}
    fieldsets = [
        ("Identity", {"fields": ["key", "name", "domain"]}),
        ("Hero", {"fields": ["headline", "subline", "cta"]}),
        ("Lists", {"fields": ["nav", "cards"], "description": "One item per line; three fit the mockup best."}),
        ("Colours", {"fields": ["accent", "accent_dark", "soft"], "classes": ["collapse"]}),
        ("Placement", {"fields": ["order", "is_published"]}),
    ]

    @admin.display(description="used by")
    def used_by(self, obj):
        names = [i.name for i in obj.industries.all()] + [p.title for p in obj.projects.all()]
        return ", ".join(names) or "—"


class IndustryInline(admin.TabularInline):
    model = Industry
    extra = 0
    fields = ["name", "template_industry", "order", "is_published"]
    ordering = ["order", "id"]
    show_change_link = True


@admin.register(IndustriesSection)
class IndustriesSectionAdmin(admin.ModelAdmin):
    list_display = ["heading", "updated_at"]
    fieldsets = [
        ("Heading", {"fields": ["heading"]}),
        ("Per-tab link", {"fields": ["link_label", "link_href"]}),
        ("Footnote", {"fields": ["footnote_label", "footnote_items"]}),
    ]

    def has_add_permission(self, request):
        return not IndustriesSection.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Industry)
class IndustryAdmin(OrderedAdmin):
    display_columns = ["name", "slug", "template_industry"]
    list_filter = ["is_published", "template_industry"]
    search_fields = ["name", "pitch", "features"]
    prepopulated_fields = {"slug": ["name"]}
    autocomplete_fields = ["template_industry"]
    fieldsets = [
        ("Industry", {"fields": ["name", "slug", "pitch", "features"]}),
        ("Demo preview", {"fields": ["template_industry"]}),
        ("Placement", {"fields": ["order", "is_published"]}),
    ]


@admin.register(Project)
class ProjectAdmin(OrderedAdmin):
    display_columns = ["title", "category", "template_project"]
    list_filter = ["is_published", "template_project"]
    search_fields = ["title", "category", "description"]
    autocomplete_fields = ["template_project"]
    fieldsets = [
        ("Project", {"fields": ["title", "category", "description", "features"]}),
        ("Demo preview", {"fields": ["template_project"]}),
        ("Placement", {"fields": ["order", "is_published"]}),
    ]


@admin.register(ProcessStep)
class ProcessStepAdmin(OrderedAdmin):
    display_columns = ["title"]


@admin.register(Package)
class PackageAdmin(OrderedAdmin):
    display_columns = ["name", "tagline"]
    search_fields = ["name", "tagline", "features"]


@admin.register(Testimonial)
class TestimonialAdmin(OrderedAdmin):
    display_columns = ["name", "business"]
    search_fields = ["name", "business", "quote"]


@admin.register(FaqItem)
class FaqItemAdmin(OrderedAdmin):
    display_columns = ["question"]
    search_fields = ["question", "answer"]


@admin.register(TeamMember)
class TeamMemberAdmin(OrderedAdmin):
    display_columns = ["name", "role"]
    search_fields = ["name", "role", "bio"]
    fieldsets = [
        ("Person", {"fields": ["name", "role", "bio", "photo"]}),
        ("Contact and socials", {"fields": ["email", "whatsapp", "linkedin", "facebook", "instagram"],
                                 "description": "Only the ones you fill in are shown."}),
        ("Placement", {"fields": ["order", "is_published"]}),
    ]
