from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health(_request):
    """Cheap liveness probe for the host/uptime checks."""
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("enquiries.urls")),
    path("api/", include("content.urls")),
    path("api/health/", health, name="health"),
]

if settings.DEBUG:
    # Django only serves uploads during development.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
