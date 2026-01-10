from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite
from django.utils import timezone
from elections.models import Candidate, Position, Election
from voting.models import QRLink


class AdminIssueSignedLinkTests(TestCase):
    def setUp(self):
        now = timezone.now()
        self.election = Election.objects.create(name='Admin QR Election', start_time=now, end_time=now)
        self.position = Position.objects.create(election=self.election, name='President')
        self.candidate = Candidate.objects.create(position=self.position, name='Admin Bob')
        User = get_user_model()
        self.user = User.objects.create_user(username='target_user', password='pass')
        self.admin = User.objects.create_superuser(username='admin', email='admin@example.com', password='adminpass')
        # force login as admin
        self.client.force_login(self.admin)

    def test_issue_signed_link_form_creates_qrlink(self):
        url = reverse('admin:elections_candidate_issue_signed_link', args=[self.candidate.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # submit the form with a 5 minute TTL
        resp = self.client.post(url, {'user': self.user.id, 'ttl_minutes': 5})
        # after successful creation a preview page with the signed link should be shown
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(QRLink.objects.filter(user=self.user, candidate=self.candidate).exists())
        ql = QRLink.objects.get(user=self.user, candidate=self.candidate)
        self.assertIsNotNone(ql.token)
        self.assertIsNotNone(ql.token_hash)
        self.assertIsNotNone(ql.expires_at)
        content = resp.content.decode('utf-8')
        # the signed token should appear on the preview page
        self.assertIn(ql.token, content)
        # the qr image src should contain the signed link (via chart API)
        self.assertIn('chart.googleapis.com', content)
