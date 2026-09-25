from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SECTION_VIEWSETS, SiteContentView

router = DefaultRouter()
for key, viewset in SECTION_VIEWSETS.items():
    # "processSteps" -> "process-steps" so URLs stay kebab-case.
    slug = "".join(f"-{c.lower()}" if c.isupper() else c for c in key)
    router.register(slug, viewset, basename=slug)

urlpatterns = [
    path("content/", SiteContentView.as_view(), name="site-content"),
    path("content/", include(router.urls)),
]
