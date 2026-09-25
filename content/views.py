from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    DigitalExperiencesSection,
    IndustriesSection,
    Template,
    FaqItem,
    HeroSection,
    Industry,
    Package,
    Problem,
    ProcessStep,
    Project,
    SiteSettings,
    Stat,
    TeamMember,
    Testimonial,
    YourIdeaSection,
)
from .serializers import (
    DigitalExperiencesSerializer,
    IndustriesSectionSerializer,
    TemplateSerializer,
    FaqItemSerializer,
    HeroSectionSerializer,
    IndustrySerializer,
    PackageSerializer,
    ProblemSerializer,
    ProcessStepSerializer,
    ProjectSerializer,
    SiteSettingsSerializer,
    StatSerializer,
    TeamMemberSerializer,
    TestimonialSerializer,
    YourIdeaSerializer,
)

# One place defining every published list, so the aggregate endpoint and the
# per-model endpoints can never drift apart.
CONTENT_SECTIONS = [
    ("stats", Stat, StatSerializer),
    ("problems", Problem, ProblemSerializer),
    ("templates", Template, TemplateSerializer),
    ("industries", Industry, IndustrySerializer),
    ("projects", Project, ProjectSerializer),
    ("processSteps", ProcessStep, ProcessStepSerializer),
    ("packages", Package, PackageSerializer),
    ("team", TeamMember, TeamMemberSerializer),
    ("testimonials", Testimonial, TestimonialSerializer),
    ("faqs", FaqItem, FaqItemSerializer),
]


class SiteContentView(APIView):
    """The whole site's copy in one response.

    The frontend renders entire pages at once, so a single request keeps it to
    one network round trip and one cache entry.
    """

    def get(self, _request):
        # Singletons first; the rest are published lists.
        payload = {
            "site": SiteSettingsSerializer(SiteSettings.load()).data,
            "hero": HeroSectionSerializer(HeroSection.load(), context={"request": _request}).data,
            "yourIdea": YourIdeaSerializer(YourIdeaSection.load()).data,
            "digitalExperiences": DigitalExperiencesSerializer(DigitalExperiencesSection.load()).data,
            "industriesSection": IndustriesSectionSerializer(IndustriesSection.load()).data,
        }
        for key, model, serializer in CONTENT_SECTIONS:
            payload[key] = serializer(model.objects.published(), many=True, context={"request": _request}).data
        return Response(payload)


def _readonly_viewset(model, serializer):
    """Per-model list/detail endpoints, for anything that needs one slice."""

    return type(
        f"{model.__name__}ViewSet",
        (viewsets.ReadOnlyModelViewSet,),
        {
            "queryset": model.objects.published(),
            "serializer_class": serializer,
            "pagination_class": None,
        },
    )


SECTION_VIEWSETS = {key: _readonly_viewset(model, serializer) for key, model, serializer in CONTENT_SECTIONS}
