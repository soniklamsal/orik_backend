from rest_framework import generics
from rest_framework.throttling import AnonRateThrottle

from .models import Enquiry
from .serializers import EnquirySerializer


class EnquiryRateThrottle(AnonRateThrottle):
    """Rate limited per IP; the rate itself lives in settings."""

    scope = "enquiries"


class EnquiryCreateView(generics.CreateAPIView):
    """Accepts contact-form submissions. Write-only: enquiries are read in the admin."""

    queryset = Enquiry.objects.all()
    serializer_class = EnquirySerializer
    throttle_classes = [EnquiryRateThrottle]

    def perform_create(self, serializer):
        serializer.save(
            ip_address=client_ip(self.request),
            user_agent=self.request.META.get("HTTP_USER_AGENT", "")[:300],
        )


def client_ip(request):
    """Real client IP, accounting for a single proxy in front of the API."""
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")
