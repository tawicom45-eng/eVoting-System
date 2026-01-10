from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from analytics.models import Metric
from django.utils import timezone


class MetricViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        Metric.objects.create(name="m1", value=1.5)
        Metric.objects.create(name="m1", value=2.5)
        Metric.objects.create(name="m2", value=10.0)

    def test_metric_list_filter_name(self):
        url = reverse("metrics-list")
        resp = self.client.get(url + "?name=m1")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 2)

    def test_metric_aggregate_requires_name(self):
        url = reverse("metrics-aggregate")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 400)

    def test_metric_aggregate_avg(self):
        url = reverse("metrics-aggregate")
        resp = self.client.get(url + "?name=m1")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("avg", data)
        self.assertAlmostEqual(data["avg"], 2.0)
