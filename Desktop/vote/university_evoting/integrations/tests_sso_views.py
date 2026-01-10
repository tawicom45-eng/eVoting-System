from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from accounts.models import Profile
from elections.models import Election, Position, Candidate
from voting.models import EncryptedVote
from voting.utils_qr import generate_signed_qr_token


class SSOVewwTests(TestCase):
    def setUp(self):
        now = timezone.now()
        self.election = Election.objects.create(name="SSO Election", start_time=now, end_time=now)
        self.position = Position.objects.create(election=self.election, name="President")
        self.candidate = Candidate.objects.create(position=self.position, name="SSO Alice")

    def test_sso_login_creates_and_authenticates_user_and_allows_cast(self):
        confirm = reverse('voting-qr-confirm', kwargs={'qr_slug': self.candidate.qr_slug})
        sso_login = reverse('integrations-sso-login') + f"?next={confirm}"
        # follow redirect to confirm
        resp = self.client.get(sso_login, follow=True)
        self.assertEqual(resp.status_code, 200)
        user = resp.context['user']
        self.assertTrue(user.is_authenticated)
        self.assertEqual(user.username, 'sso_alice')
        # POST to confirm to cast
        resp = self.client.post(confirm)
        # should redirect to success
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(EncryptedVote.objects.filter(candidate=self.candidate).exists())

    def test_sso_login_with_signed_token_auto_casts(self):
        # Pre-create the user that DummySSOAdapter will return so token is issued for that user id
        User = get_user_model()
        sso_user = User.objects.create_user(username='sso_alice', email='sso_alice@example.com')
        sso_user.set_unusable_password()
        sso_user.save()
        Profile.objects.create(user=sso_user, student_id='SSO01', role='student')

        token = generate_signed_qr_token(sso_user.id, self.candidate.id)
        confirm = reverse('voting-qr-confirm', kwargs={'qr_slug': self.candidate.qr_slug}) + f"?token={token}"
        sso_login = reverse('integrations-sso-login') + f"?next={confirm}"
        # follow SSO login redirect to confirm (should be auto-cast)
        resp = self.client.get(sso_login, follow=True)
        # Following redirects should end up at confirmation or success; if auto-cast occurred expect final redirect to success
        # Ensure the user is authenticated
        user = resp.context.get('user') if resp.context else None
        if user:
            self.assertTrue(user.is_authenticated)
        # Now ensure the signed token resulted in a cast (EncryptedVote exists)
        self.assertTrue(EncryptedVote.objects.filter(candidate=self.candidate).exists())
