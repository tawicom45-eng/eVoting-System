from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from unittest.mock import patch


class QRLoginTests(TestCase):

    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user(username='admin', password='pass', is_staff=True)
        self.user = User.objects.create_user(username='qruser', password='pass')
        self.client = Client()

    def test_admin_issue_and_verify_qr_login(self):
        # admin issue token
        self.client.login(username='admin', password='pass')
        res = self.client.post('/api/accounts/qr/login/issue/', {'user_id': self.user.id})
        self.assertEqual(res.status_code, 201)
        token = res.json().get('token')
        self.assertIsNotNone(token)
        # verify token (public)
        res2 = self.client.post('/api/accounts/qr/login/verify/', {'token': token})
        self.assertEqual(res2.status_code, 200)
        data = res2.json()
        self.assertIn('access_token', data)
        self.assertIn('refresh_token', data)

    def test_replay_prevention(self):
        self.client.login(username='admin', password='pass')
        res = self.client.post('/api/accounts/qr/login/issue/', {'user_id': self.user.id})
        token = res.json().get('token')
        res1 = self.client.post('/api/accounts/qr/login/verify/', {'token': token})
        self.assertEqual(res1.status_code, 200)
        res2 = self.client.post('/api/accounts/qr/login/verify/', {'token': token})
        self.assertIn(res2.status_code, (400, 404))