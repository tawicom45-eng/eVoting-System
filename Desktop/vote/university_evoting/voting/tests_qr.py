from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from elections.models import Election, Position, Candidate
from accounts.models import Profile
from voting.models import VoteToken, EncryptedVote
from django.utils import timezone


class QRCastTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="voter", password="pass")
        # ensure a Profile exists for ABAC evaluation
        Profile.objects.create(user=self.user, student_id="V001", role="student")
        now = timezone.now()
        self.election = Election.objects.create(name="QR Election", start_time=now, end_time=now)
        self.position = Position.objects.create(election=self.election, name="President")
        self.candidate = Candidate.objects.create(position=self.position, name="Alice")

    def test_qr_cast_requires_auth(self):
        url = reverse('api-qr-cast', kwargs={'qr_slug': self.candidate.qr_slug})
        resp = self.client.get(url)
        # Depending on auth configuration, unauthenticated may return 401 or 403; accept either
        self.assertIn(resp.status_code, (401, 403))

    def test_qr_cast_creates_vote_for_authenticated_user(self):
        # test full browser flow: landing -> login -> confirm -> success
        landing = reverse('voting-qr-landing', kwargs={'qr_slug': self.candidate.qr_slug})
        resp = self.client.get(landing)
        self.assertEqual(resp.status_code, 200)
        self.client.login(username="voter", password="pass")
        confirm = reverse('voting-qr-confirm', kwargs={'qr_slug': self.candidate.qr_slug})
        # GET confirm page
        resp = self.client.get(confirm)
        self.assertEqual(resp.status_code, 200)
        # POST to confirm to cast
        resp = self.client.post(confirm)
        # After redirect to success
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(EncryptedVote.objects.filter(candidate=self.candidate).exists())
        token = VoteToken.objects.get(user=self.user, election=self.election)
        self.assertTrue(token.used)

    def test_qr_cast_abac_denies(self):
        # mark user suspended
        self.user.profile.status = Profile.STATUS_SUSPENDED
        self.user.profile.save()
        self.client.login(username="voter", password="pass")
        confirm = reverse('voting-qr-confirm', kwargs={'qr_slug': self.candidate.qr_slug})
        resp = self.client.post(confirm)
        self.assertEqual(resp.status_code, 403)
