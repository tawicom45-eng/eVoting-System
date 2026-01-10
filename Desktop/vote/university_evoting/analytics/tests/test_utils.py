from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from analytics.utils import record_metric, aggregate_average
from analytics.models import Metric


class MetricUtilsTests(TestCase):
    def test_record_metric_and_aggregate(self):
        # Ensure record_metric stores a metric and aggregate_average computes correctly
        now = timezone.now()
        record_metric("test_metric", 1.0)
        record_metric("test_metric", 3.0)
        avg = aggregate_average("test_metric")
        self.assertAlmostEqual(avg, 2.0)

    def test_aggregate_with_window(self):
        # Create an old metric beyond window and a recent one
        old = Metric.objects.create(name="temp", value=10.0, recorded_at=timezone.now() - timedelta(seconds=3600))
        recent = Metric.objects.create(name="temp", value=2.0, recorded_at=timezone.now())
        avg_all = aggregate_average("temp")
        avg_window = aggregate_average("temp", window_seconds=60)
        self.assertAlmostEqual(avg_all, 6.0)
        self.assertAlmostEqual(avg_window, 2.0)
