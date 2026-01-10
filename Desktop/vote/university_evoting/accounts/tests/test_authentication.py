from django.test import TestCase, override_settings
from types import SimpleNamespace
import uuid
import hmac
import hashlib
from django.conf import settings
from accounts.authentication import _verify_signature, JTIAuthentication
from accounts.models import AuthSession, RevokedAccessToken
from django.contrib.auth import get_user_model


class JTIAuthTests(TestCase):

    def test_verify_signature(self):
        jti = str(uuid.uuid4())
        secret = 'test-secret'
        sig = hmac.new(secret.encode('utf-8'), jti.encode('utf-8'), hashlib.sha256).hexdigest()
        with override_settings(ACCESS_TOKEN_SECRET=secret):
            self.assertTrue(_verify_signature(jti, sig))

    def test_authenticate_returns_user_on_valid_token(self):
        User = get_user_model()
        user = User.objects.create_user(username='alice', password='pass')
        session = AuthSession.objects.create(user=user)
        revoked_obj = RevokedAccessToken.objects.create(session=session)
        jti = str(revoked_obj.jti)
        # compute signature with current settings
        secret = getattr(settings, 'ACCESS_TOKEN_SECRET', 'dev-access-secret')
        sig = hmac.new(secret.encode('utf-8'), jti.encode('utf-8'), hashlib.sha256).hexdigest()
        token = f"{jti}.{sig}"
        req = SimpleNamespace(META={'HTTP_AUTHORIZATION': f'Bearer {token}'})
        auth = JTIAuthentication()
        user_res = auth.authenticate(req)
        self.assertIsNotNone(user_res)
        user_obj, token_str = user_res
        self.assertEqual(user_obj.id, user.id)

    def test_authenticate_none_if_revoked(self):
        User = get_user_model()
        user = User.objects.create_user(username='bob', password='pass')
        session = AuthSession.objects.create(user=user)
        revoked_obj = RevokedAccessToken.objects.create(session=session, revoked=True)
        jti = str(revoked_obj.jti)
        secret = getattr(settings, 'ACCESS_TOKEN_SECRET', 'dev-access-secret')
        sig = hmac.new(secret.encode('utf-8'), jti.encode('utf-8'), hashlib.sha256).hexdigest()
        token = f"{jti}.{sig}"
        req = SimpleNamespace(META={'HTTP_AUTHORIZATION': f'Bearer {token}'})
        auth = JTIAuthentication()
        res = auth.authenticate(req)
        self.assertIsNone(res)

    def test_invalid_format_raises(self):
        req = SimpleNamespace(META={'HTTP_AUTHORIZATION': 'Bearer invalidformat'})
        auth = JTIAuthentication()
        from rest_framework import exceptions
        with self.assertRaises(exceptions.AuthenticationFailed):
            auth.authenticate(req)
