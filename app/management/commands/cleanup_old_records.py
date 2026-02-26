from django.core.management.base import BaseCommand

from app.views import _run_cleanup


class Command(BaseCommand):
    help = "Delete old emergency/chatbot logs and media files."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=30)

    def handle(self, *args, **options):
        days = options["days"]
        alert_count, log_count = _run_cleanup(days=days)
        self.stdout.write(self.style.SUCCESS(f"Cleanup done: alerts={alert_count}, logs={log_count}, days={days}"))
