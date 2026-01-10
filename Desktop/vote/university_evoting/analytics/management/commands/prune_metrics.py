from django.core.management.base import BaseCommand
from analytics.models import Metric
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Prune metrics older than provided days (default 30)'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=30, help='Number of days to keep')

    def handle(self, *args, **options):
        days = options['days']
        # Use date comparison to be robust to timezone-aware vs naive datetimes
        cutoff_date = (timezone.now() - timedelta(days=days)).date()
        qs = Metric.objects.filter(recorded_at__date__lt=cutoff_date)
        count = qs.count()
        qs.delete()
        self.stdout.write(self.style.SUCCESS(f'Pruned {count} metrics older than {days} days'))
