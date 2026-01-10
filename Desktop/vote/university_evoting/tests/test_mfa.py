from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from accounts.models import Profile, MFATOTPDevice
import pyotp


class MFATOTPTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="bob", password="password")
        Profile.objects.create(user=self.user, role="student", status=Profile.STATUS_ACTIVE)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_register_totp_creates_device(self):
        r = self.client.post("/api/auth/mfa/totp/register/", {"label": "bob-phone"}, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertIn("secret", r.data)
        self.assertIn("provisioning_uri", r.data)
        secret = r.data.get("secret")
        # device exists and stored encrypted but decrypts back to same secret
        devs = MFATOTPDevice.objects.filter(user=self.user)
        self.assertTrue(devs.exists())
        d = devs.first()
        self.assertEqual(d.plaintext_secret, secret)

    def test_verify_totp_confirms_device(self):
        # register
        r = self.client.post("/api/auth/mfa/totp/register/", {"label": "bob-phone"}, format="json")
        secret = r.data.get("secret")
        devs = MFATOTPDevice.objects.filter(user=self.user)
        self.assertTrue(devs.exists())
        device = devs.first()
        # ensure stored secret decrypts to what was returned
        self.assertEqual(device.plaintext_secret, secret)
        # create code
        totp = pyotp.TOTP(secret)
        token = totp.now()
        v = self.client.post("/api/auth/mfa/totp/verify/", {"device_id": device.id, "token": token}, format="json")
        self.assertEqual(v.status_code, 200)
        device.refresh_from_db()
        self.assertTrue(device.confirmed)
