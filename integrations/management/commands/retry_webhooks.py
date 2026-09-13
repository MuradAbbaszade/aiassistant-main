from django.core.management.base import BaseCommand

from integrations.services.dispatch import process_due_deliveries


class Command(BaseCommand):
    help = "Retry pending outbound CRM webhook deliveries that are due."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=100)

    def handle(self, *args, **options):
        count = process_due_deliveries(limit=options["limit"])
        self.stdout.write(self.style.SUCCESS(f"Processed {count} successful deliveries this run."))
