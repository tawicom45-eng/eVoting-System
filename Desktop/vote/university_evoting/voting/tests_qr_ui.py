from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from elections.models import Election, Position, Candidate
from accounts.models import Profile
from voting.utils_qr import generate_signed_qr_token
from django.utils import timezone


class QRConfirmUITests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="ui_voter", password="pass")
        Profile.objects.create(user=self.user, student_id="VUI1", role="student")
        now = timezone.now()
        self.election = Election.objects.create(name="UI Election", start_time=now, end_time=now)
        self.position = Position.objects.create(election=self.election, name="President")
        self.candidate = Candidate.objects.create(position=self.position, name="UI Alice")

    def test_confirm_page_has_client_js_and_shows_token_message(self):
        # create a token for another user so auto-cast does not trigger
        other = get_user_model().objects.create_user(username='other', password='x')
        token = generate_signed_qr_token(other.id, self.candidate.id)
        self.client.login(username="ui_voter", password="pass")
        confirm = reverse('voting-qr-confirm', kwargs={'qr_slug': self.candidate.qr_slug}) + f"?token={token}"
        resp = self.client.get(confirm)
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode('utf-8')
        # confirm page should include the JS hook and mention the signed token
        self.assertIn('id="confirm-form"', content)
        self.assertIn('signed token is attached', content)
