from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from accounts.models import AuthSession, RevokedAccessToken
import uuid
import hmac, hashlib
from django.conf import settings


class JTIAuthTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="tokenuser", password="p")
        self.session = AuthSession.objects.create(user=self.user)
        # create signed token
        self.jti = uuid.uuid4()
        secret = getattr(settings, 'ACCESS_TOKEN_SECRET')
        self.sig = hmac.new(secret.encode('utf-8'), str(self.jti).encode('utf-8'), hashlib.sha256).hexdigest()
        RevokedAccessToken.objects.create(jti=self.jti, session=self.session)
        self.client = Client()

    def test_valid_token_authenticates(self):
        token = f"{self.jti}.{self.sig}"
        r = self.client.get("/api/elections/", HTTP_AUTHORIZATION=f"Bearer {token}")
        # backend will authenticate and return list or 403/200 depending on endpoint, but must not be 401
        self.assertNotEqual(r.status_code, 401)

    def test_invalid_signature_rejected(self):
        token = f"{self.jti}.bad_sig"
        r = self.client.get("/api/elections/", HTTP_AUTHORIZATION=f"Bearer {token}")
        # Accept either 401 or 403 depending on auth handler behavior
        self.assertIn(r.status_code, (401, 403))

    def test_revoked_jti_rejected(self):
        # revoke the jti
        RevokedAccessToken.objects.filter(jti=self.jti).update(revoked=True)
        token = f"{self.jti}.{self.sig}"
        r = self.client.get("/api/elections/", HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertEqual(r.status_code, 401)
