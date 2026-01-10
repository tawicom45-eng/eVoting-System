from rest_framework.test import APIClient, APITestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from elections.models import Election, Position, Candidate


class QRApiTests(APITestCase):

    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user(username='admin', password='pass', is_staff=True)
        self.user = User.objects.create_user(username='voter', password='pass')
        now = timezone.now()
        self.election = Election.objects.create(name='E', start_time=now - timedelta(hours=1), end_time=now + timedelta(days=1))
        self.position = Position.objects.create(name='P', election=self.election)
        self.candidate = Candidate.objects.create(name='C', position=self.position)
        self.client = APIClient()

    def test_issue_qr_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        res = self.client.post('/api/voting/qr/api/issue/', {'user_id': self.user.id, 'candidate_id': self.candidate.id, 'ttl_minutes': 10}, format='json')
        self.assertEqual(res.status_code, 201)
        self.assertIn('token', res.data)

    def test_verify_qr_token(self):
        # issue token first
        self.client.force_authenticate(user=self.admin)
        res = self.client.post('/api/voting/qr/api/issue/', {'user_id': self.user.id, 'candidate_id': self.candidate.id}, format='json')
        token = res.data['token']
        # verify without auth
        self.client.force_authenticate(user=None)
        res2 = self.client.post('/api/voting/qr/api/verify/', {'token': token}, format='json')
        self.assertEqual(res2.status_code, 200)
        self.assertTrue(res2.data.get('valid'))
