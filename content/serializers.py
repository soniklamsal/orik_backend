"""Serializers shaped to match the TypeScript types in frontend/src/data/.

Field names are camelCase where the frontend already uses camelCase, so the
payload can be consumed without a translation layer.
"""

from rest_framework import serializers

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


class TemplateSerializer(serializers.ModelSerializer):
    """Shaped to match the frontend's MockupTheme type exactly."""

    nav = serializers.ListField(source="nav_list", child=serializers.CharField(), read_only=True)
    cards = serializers.ListField(source="card_list", child=serializers.CharField(), read_only=True)
    accentDark = serializers.CharField(source="accent_dark", read_only=True)

    class Meta:
        model = Template
        fields = ["key", "name", "domain", "headline", "subline", "cta", "nav", "cards", "accent", "accentDark", "soft"]


class IndustriesSectionSerializer(serializers.ModelSerializer):
    linkLabel = serializers.CharField(source="link_label", read_only=True)
    linkHref = serializers.CharField(source="link_href", read_only=True)
    footnoteLabel = serializers.CharField(source="footnote_label", read_only=True)
    footnoteItems = serializers.ListField(source="footnote_list", child=serializers.CharField(), read_only=True)

    class Meta:
        model = IndustriesSection
        fields = ["heading", "linkLabel", "linkHref", "footnoteLabel", "footnoteItems"]


class DigitalExperiencesSerializer(serializers.ModelSerializer):
    linkLabel = serializers.CharField(source="link_label", read_only=True)
    linkHref = serializers.CharField(source="link_href", read_only=True)

    class Meta:
        model = DigitalExperiencesSection
        fields = ["heading", "linkLabel", "linkHref"]


class YourIdeaSerializer(serializers.ModelSerializer):
    closingText = serializers.CharField(source="closing_text", read_only=True)
    ctaLabel = serializers.CharField(source="cta_label", read_only=True)
    ctaHref = serializers.CharField(source="cta_href", read_only=True)

    class Meta:
        model = YourIdeaSection
        fields = ["heading", "closingText", "ctaLabel", "ctaHref"]


class HeroBadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeroBadge
        fields = ["label", "icon"]


class HeroSectionSerializer(serializers.ModelSerializer):
    qualitiesLabel = serializers.CharField(source="qualities_label", read_only=True)
    qualities = serializers.ListField(source="quality_list", child=serializers.CharField(), read_only=True)
    image = serializers.SerializerMethodField()
    imageAlt = serializers.CharField(source="image_alt", read_only=True)
    badges = serializers.SerializerMethodField()

    class Meta:
        model = HeroSection
        fields = ["heading", "subheading", "qualitiesLabel", "qualities", "image", "imageAlt", "badges"]

    def get_image(self, obj):
        if not obj.image:
            # Empty means "keep the image bundled with the frontend".
            return ""
        request = self.context.get("request")
        return request.build_absolute_uri(obj.image.url) if request else obj.image.url

    def get_badges(self, obj):
        # An unsaved fallback hero has no related rows yet.
        badges = obj.badges.published() if obj.pk else HeroBadge.objects.none()
        return HeroBadgeSerializer(badges, many=True).data


class SocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialLink
        fields = ["platform", "label", "href"]


class SiteSettingsSerializer(serializers.ModelSerializer):
    contact = serializers.SerializerMethodField()
    socials = serializers.SerializerMethodField()

    class Meta:
        model = SiteSettings
        fields = ["name", "description", "contact", "socials"]

    def get_contact(self, obj):
        # Blank fields are omitted so the footer can hide them by absence.
        return {key: value for key, value in (("email", obj.email), ("phone", obj.phone), ("location", obj.location)) if value}

    def get_socials(self, obj):
        return SocialLinkSerializer(SocialLink.objects.published(), many=True).data


class StatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stat
        fields = ["value", "label"]


class ProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = ["title", "description"]


class IndustrySerializer(serializers.ModelSerializer):
    features = serializers.ListField(source="feature_list", child=serializers.CharField(), read_only=True)
    template = TemplateSerializer(source="template_industry", read_only=True)

    class Meta:
        model = Industry
        fields = ["name", "slug", "pitch", "features", "template"]


class ProjectSerializer(serializers.ModelSerializer):
    features = serializers.ListField(source="feature_list", child=serializers.CharField(), read_only=True)
    template = TemplateSerializer(source="template_project", read_only=True)

    class Meta:
        model = Project
        fields = ["title", "category", "description", "features", "template"]


class ProcessStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessStep
        fields = ["title", "description"]


class PackageSerializer(serializers.ModelSerializer):
    features = serializers.ListField(source="feature_list", child=serializers.CharField(), read_only=True)

    class Meta:
        model = Package
        fields = ["name", "tagline", "features"]


class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = ["quote", "name", "business"]


class FaqItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaqItem
        fields = ["question", "answer"]


class TeamMemberSerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField()
    links = serializers.ReadOnlyField()

    class Meta:
        model = TeamMember
        fields = ["name", "role", "bio", "photo", "links"]

    def get_photo(self, obj):
        if not obj.photo:
            return ""
        request = self.context.get("request")
        # Absolute, so the Next.js server can fetch it from its own process.
        return request.build_absolute_uri(obj.photo.url) if request else obj.photo.url
