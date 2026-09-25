from django.db import models


class Enquiry(models.Model):
    """A contact-form submission from the ORIK Webcraft site."""

    class Status(models.TextChoices):
        NEW = "new", "New"
        CONTACTED = "contacted", "Contacted"
        CLOSED = "closed", "Closed"

    name = models.CharField(max_length=120)
    business = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40)
    package = models.CharField(max_length=60, blank=True)
    message = models.TextField(blank=True)

    status = models.CharField(max_length=16, choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField(auto_now_add=True)

    # Kept for abuse triage only; never returned by the API.
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=300, blank=True)

    class Meta:
        verbose_name_plural = "enquiries"
        # -id breaks ties, since two enquiries can share a created_at timestamp.
        ordering = ["-created_at", "-id"]
        indexes = [models.Index(fields=["status", "-created_at"])]

    def __str__(self):
        return f"{self.name} — {self.business}"
