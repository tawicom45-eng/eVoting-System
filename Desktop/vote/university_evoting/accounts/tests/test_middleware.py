from django.test import TestCase
from types import SimpleNamespace
import uuid
from accounts.middleware import RevokedAccessTokenMiddleware
from accounts.models import AuthSession, RevokedAccessToken
from django.contrib.auth import get_user_model
from django.http import HttpResponse


class MiddlewareTests(TestCase):
    def test_revoked_token_returns_401(self):
        User = get_user_model()
        user = User.objects.create_user(username='charlie', password='pass')
        session = AuthSession.objects.create(user=user)
        revoked = RevokedAccessToken.objects.create(session=session, revoked=True)
        jti = str(revoked.jti)
        token = f"{jti}.sig"
        # dummy get_response
        def get_response(req):
            return HttpResponse('ok')
        mw = RevokedAccessTokenMiddleware(get_response)
        req = SimpleNamespace(META={'HTTP_AUTHORIZATION': f'Bearer {token}'})
        resp = mw(req)
        self.assertEqual(resp.status_code, 401)
        self.assertIn('token revoked', resp.content.decode('utf-8'))

    def test_non_revoked_allows_through(self):
        User = get_user_model()
        user = User.objects.create_user(username='dave', password='pass')
        session = AuthSession.objects.create(user=user)
        active = RevokedAccessToken.objects.create(session=session, revoked=False)
        jti = str(active.jti)
        token = f"{jti}.sig"
        def get_response(req):
            return HttpResponse('ok')
        mw = RevokedAccessTokenMiddleware(get_response)
        req = SimpleNamespace(META={'HTTP_AUTHORIZATION': f'Bearer {token}'})
        resp = mw(req)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content.decode('utf-8'), 'ok')
