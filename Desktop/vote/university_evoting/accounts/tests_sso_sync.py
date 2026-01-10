from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth import get_user_model


class SSOSyncTests(TestCase):
    def test_dummy_sso_sync_creates_users(self):
        call_command("sync_sso", "--adapter", "dummy")
        User = get_user_model()
        self.assertTrue(User.objects.filter(username="sso_alice").exists())
        self.assertTrue(User.objects.filter(username="sso_bob").exists())
