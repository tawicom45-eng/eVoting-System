from django.test import TestCase, Client
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from unittest.mock import patch

from elections.models import Election, Position, Candidate
from voting.models import VoteToken


class OneTimeVotingTests(TestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='voter1', password='pass')
        now = timezone.now()
        self.election = Election.objects.create(name='E', start_time=now - timedelta(hours=1), end_time=now + timedelta(days=1))
        self.position = Position.objects.create(name='P', election=self.election)
        self.candidate = Candidate.objects.create(name='C', position=self.position)
        self.client = Client()
        # patch ABAC evaluate to allow voting in tests
        self._patcher = patch('abac.policy.evaluate', return_value=True)
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_api_cast_single_use_token(self):
        # create token
        token_obj = VoteToken.objects.create(user=self.user, election=self.election)
        self.client.login(username='voter1', password='pass')
        data = {
            'token': str(token_obj.token),
            'position_id': self.position.id,
            'candidate_id': self.candidate.id,
        }
        # first cast should succeed
        res1 = self.client.post('/api/voting/cast/', data)
        self.assertEqual(res1.status_code, 201)

        # token should be marked used
        token_obj.refresh_from_db()
        self.assertTrue(token_obj.used)

        # second cast attempt with same token should fail
        res2 = self.client.post('/api/voting/cast/', data)
        self.assertIn(res2.status_code, (400, 403))

    def test_qr_cast_single_use(self):
        # create token
        token_obj = VoteToken.objects.create(user=self.user, election=self.election)
        self.client.login(username='voter1', password='pass')
        # call QRCastView
        res1 = self.client.get(f'/api/voting/qr/{self.candidate.qr_slug}/')
        # first call should create EncryptedVote
        self.assertEqual(res1.status_code, 201)

        # second call should indicate token already used
        res2 = self.client.get(f'/api/voting/qr/{self.candidate.qr_slug}/')
        self.assertIn(res2.status_code, (400, 403))
