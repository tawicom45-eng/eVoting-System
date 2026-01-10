from django.test import TestCase
from django.urls import reverse
from analytics.utils import record_metric, aggregate_average
from analytics.models import Metric
from monitoring import metrics


class AnalyticsTests(TestCase):
    def test_record_metric_creates_row(self):
        record_metric('test.metric', 2.5)
        m = Metric.objects.filter(name='test.metric').first()
        self.assertIsNotNone(m)
        self.assertEqual(m.value, 2.5)

    def test_monitoring_increment_persists(self):
        metrics.increment('test.increment', amount=3)
        m = Metric.objects.filter(name='test.increment').first()
        self.assertIsNotNone(m)
        self.assertEqual(m.value, 3)

    def test_metrics_api_list_and_filter(self):
        record_metric('api.metric', 1)
        record_metric('api.metric', 2)
        r = self.client.get('/api/analytics/metrics/?name=api.metric')
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertTrue(len(data) >= 2)

    def test_aggregate_average(self):
        record_metric('avg.metric', 2)
        record_metric('avg.metric', 4)
        avg = aggregate_average('avg.metric')
        self.assertAlmostEqual(avg, 3.0)

    def test_metrics_api_since_until(self):
        import datetime
        from django.utils import timezone
        now = timezone.now()
        record_metric('time.metric', 1)
        # create an older metric directly; use .update() to ensure DB-level value set
        older = Metric.objects.create(name='time.metric', value=2)
        Metric.objects.filter(pk=older.pk).update(recorded_at=(now - datetime.timedelta(days=5)))
        r = self.client.get('/api/analytics/metrics/?name=time.metric')
        self.assertEqual(r.status_code, 200)
        r2 = self.client.get('/api/analytics/metrics/?name=time.metric&since=%s' % ( (now - datetime.timedelta(days=1)).isoformat() ))
        self.assertEqual(r2.status_code, 200)
        data = r2.json()
        # the since filter should return only the recent one
        self.assertTrue(all(m['value'] == 1 for m in data))
