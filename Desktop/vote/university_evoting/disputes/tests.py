from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from elections.models import Election


class ComplaintAPITest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="voter", password="pass")
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.election = Election.objects.create(name="Test Election", start_time="2025-01-01T00:00:00Z", end_time="2025-01-02T00:00:00Z", is_published=True)

    def test_create_complaint(self):
        resp = self.client.post("/api/disputes/create/", {"election": self.election.id, "subject": "Issue", "message": "There is a problem"}, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data["subject"], "Issue")
