from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from elections.models import Election, Position, Candidate
from accounts.models import Profile
from voting.utils_qr import generate_signed_qr_token
from django.utils import timezone


class QRSignedTokenTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="voter2", password="pass")
        Profile.objects.create(user=self.user, student_id="V002", role="student")
        now = timezone.now()
        self.election = Election.objects.create(name="QR Signed Election", start_time=now, end_time=now)
        self.position = Position.objects.create(election=self.election, name="President")
        self.candidate = Candidate.objects.create(position=self.position, name="Bob")

    def test_signed_token_allows_auto_cast_after_login(self):
        token = generate_signed_qr_token(self.user.id, self.candidate.id)
        # landing with token
        landing = reverse('voting-qr-landing', kwargs={'qr_slug': self.candidate.qr_slug}) + f"?token={token}"
        resp = self.client.get(landing)
        self.assertEqual(resp.status_code, 200)
        # login and visit confirm - should auto-cast and redirect to success
        self.client.login(username="voter2", password="pass")
        confirm = reverse('voting-qr-confirm', kwargs={'qr_slug': self.candidate.qr_slug}) + f"?token={token}"
        resp = self.client.get(confirm)
        # auto-cast should redirect to success
        self.assertEqual(resp.status_code, 302)
