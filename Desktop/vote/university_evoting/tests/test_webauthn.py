from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from accounts.models import Profile, WebAuthnCredential
import base64


class WebAuthnPOCTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="erin", password="password")
        Profile.objects.create(user=self.user, role="student", status=Profile.STATUS_ACTIVE)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_register_options_and_store_state(self):
        r = self.client.post('/api/auth/webauthn/register/options/', {}, format='json')
        self.assertEqual(r.status_code, 200)
        self.assertIn('challenge', r.data)
        # session should contain state
        session = self.client.session
        self.assertIn('webauthn_register_state', session)

    def test_register_complete_poc_stores_credential(self):
        # start
        r = self.client.post('/api/auth/webauthn/register/options/', {}, format='json')
        self.assertEqual(r.status_code, 200)
        # simulate client by providing base64 credential id and public key
        cid = base64.urlsafe_b64encode(b'fake-cred-1').decode('utf-8').rstrip('=')
        pub = 'fake-pub-key'
        c = self.client.post('/api/auth/webauthn/register/complete/', {'credential_id': cid, 'public_key': pub, 'sign_count': 0}, format='json')
        self.assertEqual(c.status_code, 200)
        self.assertTrue(WebAuthnCredential.objects.filter(user=self.user, label='').exists())

    def test_auth_options_includes_credentials(self):
        # create a credential entry
        WebAuthnCredential.objects.create(user=self.user, credential_id=b'fake-cred-2', public_key='fake', sign_count=0, label='')
        # another user
        User = get_user_model()
        other = User.objects.create_user(username='fred', password='password')
        Profile.objects.create(user=other, role='student', status=Profile.STATUS_ACTIVE)
        # request options for erin
        a = self.client.post('/api/auth/webauthn/auth/options/', {'username': 'erin'}, format='json')
        self.assertEqual(a.status_code, 200)
        self.assertIn('allowCredentials', a.data)
        self.assertTrue(len(a.data['allowCredentials']) >= 1)

    def test_auth_complete_poc_accepts_valid_flag(self):
        # prepare
        WebAuthnCredential.objects.create(user=self.user, credential_id=b'fake-cred-3', public_key='fake', sign_count=0, label='')
        a = self.client.post('/api/auth/webauthn/auth/options/', {'username': 'erin'}, format='json')
        self.assertEqual(a.status_code, 200)
        # complete with simulated valid response
        resp = self.client.post('/api/auth/webauthn/auth/complete/', {'username': 'erin', 'valid': True}, format='json')
        self.assertEqual(resp.status_code, 200)
