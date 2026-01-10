from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from accounts.models import MFATOTPDevice, Profile
from cryptography.fernet import Fernet
from django.core.management import call_command


class MFATOTPEncryptionTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="dave", password="password")
        Profile.objects.create(user=self.user, role="student", status=Profile.STATUS_ACTIVE)

    def test_secret_stored_encrypted_and_decryptable(self):
        key = Fernet.generate_key().decode('utf-8')
        with override_settings(MFA_SECRET_FERNET_KEY=key):
            # create device with plaintext secret
            d = MFATOTPDevice.objects.create(user=self.user, label="dev", secret="MYPLAINTEXT")
            # stored secret should not equal plaintext and should decrypt back
            self.assertNotEqual(d.secret, "MYPLAINTEXT")
            self.assertEqual(d.plaintext_secret, "MYPLAINTEXT")

    def test_rotate_mfa_keys_reencrypts_to_new_key(self):
        old_key = Fernet.generate_key().decode('utf-8')
        new_key = Fernet.generate_key().decode('utf-8')
        # Create device encrypted with old key
        with override_settings(MFA_SECRET_FERNET_KEY=old_key):
            d = MFATOTPDevice.objects.create(user=self.user, label="dev2", secret="SOMETHING")
            orig_plain = d.plaintext_secret
            self.assertEqual(orig_plain, "SOMETHING")
        # Now simulate rotating keys: set available keys to include old, but set current key to new
        with override_settings(MFA_SECRET_FERNET_KEYS=[old_key], MFA_SECRET_FERNET_KEY=new_key):
            # run rotation command; it should be able to decrypt with old and re-encrypt with new
            call_command('rotate_mfa_keys')
            d.refresh_from_db()
            self.assertEqual(d.plaintext_secret, "SOMETHING")
