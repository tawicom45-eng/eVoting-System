from django.utils import timezone
from .models import Metric
from datetime import timedelta


def record_metric(name: str, value: float = 1.0):
    """Store a metric sample in the DB. This is a best-effort call used by monitoring
    functions to persist emitted metrics for later inspection or aggregation."""
    try:
        Metric.objects.create(name=name, value=value, recorded_at=timezone.now())
    except Exception:
        # best-effort: don't raise in production metric emission paths
        return


def aggregate_average(name: str, window_seconds: int | None = None):
    from django.db.models import Avg
    from django.utils import timezone
    qs = Metric.objects.filter(name=name)
    if window_seconds is not None:
        start = timezone.now() - timedelta(seconds=int(window_seconds))
        qs = qs.filter(recorded_at__gte=start)
    return qs.aggregate(Avg("value"))["value__avg"]
