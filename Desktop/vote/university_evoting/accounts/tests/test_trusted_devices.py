from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse


class TrustedDeviceAPITest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="tduser", password="pass")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_and_list_trusted_device(self):
        url = reverse('trusted-devices-list')
        data = {
            'name': 'My Laptop',
            'fingerprint': 'fp-12345',
        }
        resp = self.client.post(url, data, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertIn('device_id', resp.data)
        self.assertEqual(resp.data.get('name'), data['name'])
        self.assertEqual(resp.data.get('fingerprint'), data['fingerprint'])

        # list
        resp2 = self.client.get(url)
        self.assertEqual(resp2.status_code, 200)
        self.assertIsInstance(resp2.data, list)
        self.assertEqual(len(resp2.data), 1)

    def test_delete_revokes_trusted_device(self):
        # create device via API
        url = reverse('trusted-devices-list')
        data = {'name': 'Phone', 'fingerprint': 'fp-phone-1'}
        resp = self.client.post(url, data, format='json')
        self.assertEqual(resp.status_code, 201)
        device_id = resp.data.get('device_id')
        self.assertIsNotNone(device_id)

        # revoke
        delete_url = reverse('trusted-devices-delete', kwargs={'device_id': device_id})
        resp2 = self.client.delete(delete_url)
        self.assertEqual(resp2.status_code, 200)

        # ensure revoked flag true
        # fetch list; since revoked=True it should not appear
        resp3 = self.client.get(url)
        self.assertEqual(resp3.status_code, 200)
        self.assertEqual(len(resp3.data), 0)
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta


class TrustedDeviceTests(TestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='tduser', password='pass')
        self.client = Client()
        self.client.login(username='tduser', password='pass')

    def test_register_and_list_device(self):
        data = {'name': 'My Phone', 'fingerprint': 'fp123', 'trusted_until': (timezone.now() + timedelta(days=30)).isoformat()}
        res = self.client.post('/api/accounts/devices/', data)
        self.assertEqual(res.status_code, 201)
        body = res.json()
        self.assertIn('device_id', body)
        # list devices
        res2 = self.client.get('/api/accounts/devices/')
        self.assertEqual(res2.status_code, 200)
        items = res2.json()
        self.assertTrue(len(items) >= 1)

    def test_revoke_device(self):
        data = {'name': 'Work Laptop', 'fingerprint': 'fp999'}
        res = self.client.post('/api/accounts/devices/', data)
        device_id = res.json().get('device_id')
        self.assertIsNotNone(device_id)
        # revoke
        res2 = self.client.delete(f'/api/accounts/devices/{device_id}/')
        self.assertIn(res2.status_code, (204, 200))
        # ensure device no longer returned
        res3 = self.client.get('/api/accounts/devices/')
        items = res3.json()
        self.assertFalse(any(d.get('device_id') == device_id for d in items))
