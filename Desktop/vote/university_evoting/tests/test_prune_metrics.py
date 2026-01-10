from django.test import TestCase
from django.core.management import call_command
from analytics.models import Metric
from django.utils import timezone
import datetime


class PruneMetricsTests(TestCase):
    def test_prune_command_removes_old(self):
        now = timezone.now()
        # create metrics and force DB-level recorded_at so auto_now_add doesn't override
        old = Metric.objects.create(name='old', value=1)
        Metric.objects.filter(pk=old.pk).update(recorded_at=now - datetime.timedelta(days=40))
        new = Metric.objects.create(name='new', value=2)
        Metric.objects.filter(pk=new.pk).update(recorded_at=now - datetime.timedelta(days=1))
        call_command('prune_metrics', '--days', '30')
        self.assertFalse(Metric.objects.filter(name='old').exists())
        self.assertTrue(Metric.objects.filter(name='new').exists())
