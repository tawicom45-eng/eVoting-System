from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from .models import ExternalIntegration


class IntegrationsAPITest(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(username="admin", password="pass")
        ExternalIntegration.objects.create(name="sms", enabled=True)
        self.client = APIClient()

    def test_admin_can_list_integrations(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.get("/api/integrations/")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(resp.data) >= 1)
