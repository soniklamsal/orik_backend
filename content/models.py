"""Editable site content.

Everything here is copy the site owner should be able to change without a
redeploy. Design internals — the mockup themes and the navigation structure —
deliberately stay in the frontend code.
"""

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify

# The ORIK brand green, used as the default accent for every template.
BRAND_ACCENT = "#008454"
BRAND_ACCENT_DARK = "#00683e"
BRAND_SOFT = "#f0f8f5"


def split_lines(value):
    """Admin edits feature lists as one-per-line text; the API returns a list."""
    return [line.strip() for line in (value or "").splitlines() if line.strip()]


class PublishedQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True)


class OrderedContent(models.Model):
    """Shared ordering and publish switch for every content list."""

    order = models.PositiveIntegerField(default=0, help_text="Lower numbers appear first.")
    is_published = models.BooleanField(default=True, help_text="Untick to hide from the site without deleting.")

    objects = PublishedQuerySet.as_manager()

    class Meta:
        abstract = True
        # id breaks ties so two rows sharing an order never swap between requests.
        ordering = ["order", "id"]


class Template(OrderedContent):
    """A demo website mockup: the fake site shown in the Industries and Work
    previews. One library, picked from both places."""

    key = models.SlugField(
        max_length=40,
        unique=True,
        help_text="Short internal id, e.g. restaurant. Used to match the built-in designs.",
    )
    name = models.CharField(max_length=60, help_text='The demo business name, e.g. "Saffron Table".')
    domain = models.CharField(max_length=80, help_text='e.g. "saffrontable.demo".')
    headline = models.CharField(max_length=120, help_text='The big line, e.g. "Fresh flavours, served daily".')
    subline = models.CharField(max_length=200, help_text="The line under the headline.")
    cta = models.CharField(max_length=40, help_text='Button label, e.g. "Book a table".')
    nav = models.TextField(help_text="Nav links, one per line. Three fit best.")
    cards = models.TextField(help_text="Card labels, one per line. Three fit best.")

    accent = models.CharField(max_length=9, default=BRAND_ACCENT, help_text="Hex colour, e.g. #008454.")
    accent_dark = models.CharField(max_length=9, default=BRAND_ACCENT_DARK)
    soft = models.CharField(max_length=9, default=BRAND_SOFT)

    class Meta(OrderedContent.Meta):
        verbose_name = "template"
        verbose_name_plural = "templates"

    def __str__(self):
        return f"{self.name} ({self.domain})"

    @property
    def nav_list(self):
        return split_lines(self.nav)

    @property
    def card_list(self):
        return split_lines(self.cards)


class IndustriesSection(models.Model):
    """The "Built for businesses like yours." band and its tab strip."""

    heading = models.CharField(max_length=120, default="Built for businesses like yours.")
    link_label = models.CharField(max_length=60, default="Start a project")
    link_href = models.CharField(max_length=120, default="/contact")
    footnote_label = models.CharField(max_length=80, default="Every demo we build is")
    footnote_items = models.TextField(
        default="Mobile friendly\nFast & modern\nBusiness focused",
        help_text="One per line; joined with a dot on the site.",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "industries section"
        verbose_name_plural = "industries section"

    def __str__(self):
        return self.heading or "Industries section"

    def clean(self):
        if not self.pk and IndustriesSection.objects.exists():
            raise ValidationError("This section already exists — edit it instead of adding another.")

    @classmethod
    def load(cls):
        return cls.objects.first() or cls()

    @property
    def footnote_list(self):
        return split_lines(self.footnote_items)


class SiteSettings(models.Model):
    """Single row of site-wide details. Contact fields left blank stay hidden."""

    name = models.CharField(max_length=80, default="ORIK Webcraft")
    description = models.TextField(help_text="Used in the footer and as the site meta description.")
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    location = models.CharField(max_length=120, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "site settings"
        verbose_name_plural = "site settings"

    def __str__(self):
        return self.name

    def clean(self):
        if not self.pk and SiteSettings.objects.exists():
            raise ValidationError("Site settings already exist — edit the existing row instead of adding another.")

    @classmethod
    def load(cls):
        return cls.objects.first() or cls(description="")


class HeroSection(models.Model):
    """The home page hero. One row; layout and animation stay in the frontend."""

    heading = models.CharField(max_length=160)
    subheading = models.TextField()

    qualities_label = models.CharField(
        max_length=60,
        default="Every ORIK website is:",
        help_text="Small label on the card under the paragraph.",
    )
    qualities = models.TextField(
        default="Mobile\nFast\nModern",
        help_text="One per line. Three short words fit the card best.",
    )

    image = models.ImageField(
        upload_to="hero/",
        blank=True,
        help_text="Showcase image. Leave blank to keep the built-in one.",
    )
    image_alt = models.CharField(
        max_length=160,
        blank=True,
        help_text="Describes the image for screen readers. Required if you upload one.",
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "hero section"
        verbose_name_plural = "hero section"

    def __str__(self):
        return self.heading or "Hero section"

    def clean(self):
        if not self.pk and HeroSection.objects.exists():
            raise ValidationError("A hero section already exists — edit it instead of adding another.")
        if self.image and not self.image_alt.strip():
            raise ValidationError({"image_alt": "Describe the image so screen readers can announce it."})

    @classmethod
    def load(cls):
        return cls.objects.first() or cls()

    @property
    def quality_list(self):
        return split_lines(self.qualities)


class HeroBadge(OrderedContent):
    """A floating pill over the hero image. Position and animation come from the
    frontend by order, so only the wording and icon are editable."""

    ICONS = [
        ("enquiries", "Rising enquiries"),
        ("whatsapp", "WhatsApp"),
        ("mobile", "Mobile"),
        ("seo", "Search / SEO"),
        ("speed", "Speed"),
        ("target", "Target"),
    ]

    hero = models.ForeignKey(HeroSection, related_name="badges", on_delete=models.CASCADE)
    label = models.CharField(max_length=40)
    icon = models.CharField(max_length=20, choices=ICONS, default="enquiries")

    class Meta(OrderedContent.Meta):
        verbose_name = "hero badge"
        verbose_name_plural = "hero badges"

    def __str__(self):
        return self.label


class SocialLink(OrderedContent):
    PLATFORMS = [
        ("twitter", "Twitter"),
        ("facebook", "Facebook"),
        ("youtube", "YouTube"),
        ("linkedin", "LinkedIn"),
        ("medium", "Medium"),
    ]

    platform = models.CharField(max_length=20, choices=PLATFORMS, unique=True)
    label = models.CharField(max_length=40)
    href = models.URLField(blank=True, help_text="Leave blank until the profile exists; blank links are hidden.")

    def __str__(self):
        return self.label


class DigitalExperiencesSection(models.Model):
    """The yellow band: a headline, a text link, and the counting stats."""

    heading = models.TextField(help_text="Line breaks are kept on wide screens.")
    link_label = models.CharField(max_length=60, default="Get a free consultation")
    link_href = models.CharField(max_length=120, default="/contact", help_text='A path such as "/contact".')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "digital experiences"
        verbose_name_plural = "digital experiences"

    def __str__(self):
        return self.heading.replace("\n", " ")[:60] or "Digital experiences"

    def clean(self):
        if not self.pk and DigitalExperiencesSection.objects.exists():
            raise ValidationError("This section already exists — edit it instead of adding another.")

    @classmethod
    def load(cls):
        return cls.objects.first() or cls(heading="")


class Stat(OrderedContent):
    """One counting figure in the "Digital experiences" band."""

    section = models.ForeignKey(
        DigitalExperiencesSection,
        related_name="stats",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Set automatically; stats are edited inside the section.",
    )
    value = models.CharField(max_length=16, help_text='Shown large, e.g. "10+" or "24/7".')
    label = models.CharField(max_length=80)

    def __str__(self):
        return f"{self.value} {self.label}"


class YourIdeaSection(models.Model):
    """The section under the hero, headed "Your business deserves more…".

    Named after the sticker that sits above it. One row; the problem cards
    below belong to it.
    """

    heading = models.TextField(help_text="Line breaks are kept on wide screens.")
    closing_text = models.TextField(help_text="The line under the cards.")
    cta_label = models.CharField(max_length=60, default="Get a free consultation")
    cta_href = models.CharField(max_length=120, default="/contact", help_text='A path such as "/contact".')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "your idea"
        verbose_name_plural = "your idea"

    def __str__(self):
        return self.heading.replace("\n", " ")[:60] or "Your idea"

    def clean(self):
        if not self.pk and YourIdeaSection.objects.exists():
            raise ValidationError("This section already exists — edit it instead of adding another.")

    @classmethod
    def load(cls):
        return cls.objects.first() or cls(heading="", closing_text="")


class Problem(OrderedContent):
    """One of the three cards in the "Your idea" section."""

    section = models.ForeignKey(
        YourIdeaSection,
        related_name="problems",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Set automatically; cards are edited inside the section.",
    )
    title = models.CharField(max_length=80)
    description = models.TextField()

    def __str__(self):
        return self.title


class Industry(OrderedContent):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True, blank=True, help_text="Used in /industries?industry=<slug>.")
    pitch = models.TextField()
    features = models.TextField(help_text="One per line.")
    template_industry = models.ForeignKey(
        Template,
        related_name="industries",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="template",
        help_text="Which demo mockup to show in the preview.",
    )

    class Meta(OrderedContent.Meta):
        verbose_name_plural = "industries"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def feature_list(self):
        return split_lines(self.features)


class Project(OrderedContent):
    title = models.CharField(max_length=80)
    category = models.CharField(max_length=80, help_text='e.g. "E-commerce website".')
    description = models.TextField()
    features = models.TextField(help_text="One per line.")
    template_project = models.ForeignKey(
        Template,
        related_name="projects",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="template",
        help_text="Which demo mockup to show in the preview.",
    )

    def __str__(self):
        return self.title

    @property
    def feature_list(self):
        return split_lines(self.features)


class ProcessStep(OrderedContent):
    title = models.CharField(max_length=60)
    description = models.TextField()

    def __str__(self):
        return self.title


class Package(OrderedContent):
    name = models.CharField(max_length=60)
    tagline = models.CharField(max_length=160)
    features = models.TextField(help_text="One per line.")

    def __str__(self):
        return self.name

    @property
    def feature_list(self):
        return split_lines(self.features)


class Testimonial(OrderedContent):
    quote = models.TextField()
    name = models.CharField(max_length=80)
    business = models.CharField(max_length=80)

    def __str__(self):
        return f"{self.name} — {self.business}"


class FaqItem(OrderedContent):
    question = models.CharField(max_length=200)
    answer = models.TextField()

    class Meta(OrderedContent.Meta):
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question


class TeamMember(OrderedContent):
    """A person on the team, shown on /team."""

    name = models.CharField(max_length=80)
    role = models.CharField(max_length=80, help_text='Job title, e.g. "Founder" or "Designer".')
    bio = models.TextField(blank=True, help_text="Optional one or two lines shown under the role.")
    photo = models.ImageField(upload_to="team/", blank=True, help_text="Portrait. Leave blank to show initials instead.")

    email = models.EmailField(blank=True)
    whatsapp = models.CharField(max_length=40, blank=True, help_text="Number in international format, e.g. +9779800000000.")
    linkedin = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)

    def __str__(self):
        return f"{self.name} — {self.role}"

    @property
    def links(self):
        """Only the socials that are filled in, in display order."""
        pairs = [
            ("linkedin", self.linkedin),
            ("facebook", self.facebook),
            ("instagram", self.instagram),
            ("whatsapp", f"https://wa.me/{self.whatsapp.lstrip('+').replace(' ', '')}" if self.whatsapp else ""),
            ("email", f"mailto:{self.email}" if self.email else ""),
        ]
        return [{"platform": platform, "href": href} for platform, href in pairs if href]
