from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import logging

from background_task.models import CompletedTask

logger = logging.getLogger('labelbase')

class Command(BaseCommand):
    help = "Remove completed tasks after 1 day."

    def handle(self, *args, **options):
        try:
            threshold = timezone.now() - timedelta(days=1)
            deleted_count, _ = CompletedTask.objects.filter(locked_at__lte=threshold).delete()
            self.stdout.write(self.style.SUCCESS(f"Deleted {deleted_count} completed tasks."))
        except Exception as ex:
            logger.exception("Error occurred while deleting completed tasks")
            self.stdout.write(self.style.ERROR("An error occurred while deleting completed tasks."))
