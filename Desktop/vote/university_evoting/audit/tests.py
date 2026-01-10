from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from .models import AuditLog


class AuditAPITest(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(username="admin", password="pass")
        AuditLog.objects.create(action="test", meta="{}")
        self.client = APIClient()

    def test_admin_can_list(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.get("/api/audit/")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(resp.data) >= 1)
