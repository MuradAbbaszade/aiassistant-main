"""Create or update a Django superuser from env vars (for hosts without a shell)."""
from __future__ import annotations

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Ensure a superuser exists from DJANGO_SUPERUSER_EMAIL / "
        "DJANGO_SUPERUSER_PASSWORD (optional DJANGO_SUPERUSER_USERNAME)."
    )

    def handle(self, *args, **options):
        email = (os.environ.get("DJANGO_SUPERUSER_EMAIL") or "").strip()
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD") or ""
        username = (os.environ.get("DJANGO_SUPERUSER_USERNAME") or email or "").strip()

        if not email or not password:
            self.stdout.write(
                self.style.WARNING(
                    "Skipped ensure_superuser: set DJANGO_SUPERUSER_EMAIL and "
                    "DJANGO_SUPERUSER_PASSWORD on Render."
                )
            )
            return

        if not username:
            username = email

        User = get_user_model()
        user = User.objects.filter(email__iexact=email).first()
        if user is None:
            user = User.objects.filter(username__iexact=username).first()

        if user is None:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
            )
            self.stdout.write(self.style.SUCCESS(f"Created superuser {email}"))
            return

        user.username = username
        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save()
        self.stdout.write(self.style.SUCCESS(f"Updated superuser {email}"))
