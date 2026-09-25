"""Create the admin login on first deploy, from environment variables.

Django's own `createsuperuser --noinput` errors when the user already exists,
which would fail every deploy after the first. This is safe to re-run: it
creates the account once and then leaves it alone, so a password changed in the
admin is never reset by a deploy.
"""

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create a superuser from DJANGO_SUPERUSER_* if one does not exist yet."

    def handle(self, *args, **options):
        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "").strip()
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "").strip()
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "").strip()

        if not username or not password:
            # Local builds have no reason to set these.
            self.stdout.write("No DJANGO_SUPERUSER_USERNAME/PASSWORD set — skipping.")
            return

        User = get_user_model()
        if User.objects.filter(username=username).exists():
            self.stdout.write(f"Superuser {username!r} already exists — left as is.")
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Created superuser {username!r}."))
