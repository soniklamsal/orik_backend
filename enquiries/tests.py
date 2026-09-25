from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import Enquiry

VALID = {
    "name": "Sonik Lamsal",
    "business": "Corner Bakery",
    "email": "owner@cornerbakery.test",
    "phone": "+977 9800000000",
    "package": "Business",
    "message": "We want online ordering.",
}


class EnquiryApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("enquiry-create")
        # Throttle counters live in the cache and would otherwise leak between tests.
        cache.clear()

    def post(self, payload, **kwargs):
        return self.client.post(self.url, payload, format="json", **kwargs)

    def test_valid_submission_is_stored(self):
        response = self.post(VALID)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        enquiry = Enquiry.objects.get()
        self.assertEqual(enquiry.business, "Corner Bakery")
        self.assertEqual(enquiry.status, Enquiry.Status.NEW)

    def test_optional_fields_may_be_omitted(self):
        payload = {k: v for k, v in VALID.items() if k not in {"package", "message"}}
        self.assertEqual(self.post(payload).status_code, status.HTTP_201_CREATED)

    def test_missing_required_field_is_rejected(self):
        payload = {**VALID}
        del payload["email"]
        response = self.post(payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertEqual(Enquiry.objects.count(), 0)

    def test_invalid_email_is_rejected(self):
        response = self.post({**VALID, "email": "not-an-email"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Enquiry.objects.count(), 0)

    def test_honeypot_blocks_bots(self):
        response = self.post({**VALID, "website": "http://spam.example"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Enquiry.objects.count(), 0)

    def test_empty_honeypot_is_fine_and_not_stored(self):
        response = self.post({**VALID, "website": ""})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(hasattr(Enquiry.objects.get(), "website"))

    def test_overlong_message_is_rejected(self):
        response = self.post({**VALID, "message": "x" * 4001})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_response_never_leaks_triage_fields(self):
        response = self.post(VALID)
        self.assertNotIn("ip_address", response.data)
        self.assertNotIn("user_agent", response.data)
        self.assertNotIn("website", response.data)

    def test_client_ip_is_recorded_from_proxy_header(self):
        self.post(VALID, HTTP_X_FORWARDED_FOR="203.0.113.9, 10.0.0.1")
        self.assertEqual(Enquiry.objects.get().ip_address, "203.0.113.9")

    def test_rate_limit_blocks_a_flood(self):
        # Matches the configured default of 5/hour per IP.
        codes = [self.post(VALID).status_code for _ in range(6)]

        self.assertEqual(codes[:5], [status.HTTP_201_CREATED] * 5)
        self.assertEqual(codes[5], status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(Enquiry.objects.count(), 5)


class EnquiryModelTests(TestCase):
    def test_str_identifies_the_sender(self):
        enquiry = Enquiry.objects.create(**VALID)
        self.assertEqual(str(enquiry), "Sonik Lamsal — Corner Bakery")

    def test_newest_first(self):
        Enquiry.objects.create(**{**VALID, "name": "First"})
        Enquiry.objects.create(**{**VALID, "name": "Second"})
        self.assertEqual([e.name for e in Enquiry.objects.all()], ["Second", "First"])
