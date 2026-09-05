"""Validate Instagram / Meta configuration and optionally send a test DM."""
from django.core.management.base import BaseCommand

from channels.services.instagram import get_instagram_credentials, is_instagram_live, send_instagram_text


class Command(BaseCommand):
    help = "Check Instagram Messaging env config; optional --igsid to send a test DM"

    def add_arguments(self, parser):
        parser.add_argument("--igsid", default="", help="Customer Instagram-scoped ID to send a test message")
        parser.add_argument("--text", default="Hello! AI Assistant Instagram test message.")

    def handle(self, *args, **options):
        if not is_instagram_live():
            self.stdout.write(self.style.ERROR("Instagram NOT configured."))
            self.stdout.write("Set INSTAGRAM_ACCESS_TOKEN and INSTAGRAM_ACCOUNT_ID in .env")
            self.stdout.write("Full guide: docs/INSTAGRAM.md")
            return
        creds = get_instagram_credentials()
        self.stdout.write(self.style.SUCCESS("Instagram credentials loaded"))
        self.stdout.write(f"  IG account id: {creds.ig_account_id}")
        self.stdout.write(f"  API host: {creds.api_host}/{creds.graph_version}")
        self.stdout.write(f"  Business tenant: {creds.business_id}")
        self.stdout.write(f"  Verify token: {creds.verify_token}")
        self.stdout.write(f"  Token length: {len(creds.access_token)} chars")
        igsid = options["igsid"]
        if igsid:
            try:
                data = send_instagram_text(recipient_igsid=igsid, text=options["text"])
                self.stdout.write(self.style.SUCCESS(f"Sent OK: {data}"))
            except Exception as exc:
                self.stdout.write(self.style.ERROR(f"Send failed: {exc}"))
        else:
            self.stdout.write("Webhook path: /webhooks/instagram/")
            self.stdout.write("Add --igsid <id> after a customer DMs you to test outbound send.")
