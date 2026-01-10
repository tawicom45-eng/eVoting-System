from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
import time


class SessionTimeoutTests(TestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='tuser', password='pass')
        self.client = Client()

    @override_settings(SESSION_IDLE_TIMEOUT=1)
    def test_session_expires_after_idle(self):
        # login
        login = self.client.login(username='tuser', password='pass')
        self.assertTrue(login)
        # initial request updates session last_activity (use an existing public view)
        res = self.client.get('/api/voting/qr/success/')
        self.assertEqual(res.status_code, 200)
        # simulate idle by backdating last_activity in session
        s = self.client.session
        s['last_activity'] = int(timezone.now().timestamp()) - 10
        s.save()

        # next request should not return 200 (session expired -> redirect or 401)
        res2 = self.client.get('/api/voting/qr/success/')
        self.assertNotEqual(res2.status_code, 200)
