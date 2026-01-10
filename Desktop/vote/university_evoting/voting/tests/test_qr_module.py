from django.test import TestCase, override_settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta
import hashlib

from voting.utils_qr import generate_signed_qr_token, verify_signed_qr_token, token_hash
from voting.models import QRLink, QRTokenUsage
from elections.models import Candidate, Election, Position


class QRModuleTests(TestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='voter', password='pass')
        # create minimal election/candidate (supply required datetimes)
        now = timezone.now()
        self.election = Election.objects.create(name='Test Election', start_time=now - timedelta(hours=1), end_time=now + timedelta(days=1))
        self.position = Position.objects.create(name='President', election=self.election)
        self.candidate = Candidate.objects.create(name='Alice', position=self.position)

    def test_generate_and_verify_token(self):
        token = generate_signed_qr_token(self.user.id, self.candidate.id)
        data = verify_signed_qr_token(token)
        self.assertEqual(int(data['u']), int(self.user.id))
        self.assertEqual(int(data['c']), int(self.candidate.id))

    def test_qrlink_valid_and_mark_used(self):
        token = generate_signed_qr_token(self.user.id, self.candidate.id)
        th = token_hash(token)
        expires = timezone.now() + timedelta(minutes=5)
        q = QRLink.objects.create(token=token, token_hash=th, user=self.user, candidate=self.candidate, expires_at=expires)
        self.assertTrue(q.is_valid())
        q.mark_used()
        self.assertFalse(QRLink.objects.get(pk=q.pk).is_valid())

    def test_qrlink_expired(self):
        token = generate_signed_qr_token(self.user.id, self.candidate.id)
        th = token_hash(token)
        expires = timezone.now() - timedelta(minutes=5)
        q = QRLink.objects.create(token=token, token_hash=th, user=self.user, candidate=self.candidate, expires_at=expires)
        self.assertFalse(q.is_valid())

    def test_replay_prevention_unique_usage(self):
        token = generate_signed_qr_token(self.user.id, self.candidate.id)
        th = token_hash(token)
        QRTokenUsage.objects.create(token_hash=th, user=self.user, candidate=self.candidate)
        # second usage should violate unique constraint and raise
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            QRTokenUsage.objects.create(token_hash=th, user=self.user, candidate=self.candidate)
