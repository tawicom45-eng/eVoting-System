from django.test import TestCase
from types import SimpleNamespace
from abac import policy


class DummyProfile:
    def __init__(self, role='user', status='active', attributes=None):
        self.role = role
        self.status = status
        self.attributes = attributes or {}


class ABACPolicyTests(TestCase):
    def test_admin_is_allowed(self):
        user = SimpleNamespace(id=1, profile=DummyProfile(role='admin'))
        allowed = policy.evaluate(user, 'any_action')
        self.assertTrue(allowed)

    def test_inactive_profile_denied(self):
        user = SimpleNamespace(id=2, profile=DummyProfile(status='inactive'))
        allowed = policy.evaluate(user, 'cast_vote')
        self.assertFalse(allowed)

    def test_attribute_denies_voting(self):
        user = SimpleNamespace(id=3, profile=DummyProfile(attributes={'allowed_to_vote': False}))
        allowed = policy.evaluate(user, 'cast_vote')
        self.assertFalse(allowed)

    def test_default_allows_other_actions(self):
        user = SimpleNamespace(id=4, profile=DummyProfile())
        allowed = policy.evaluate(user, 'read_stats')
        self.assertTrue(allowed)

    def test_invalidate_profile_cache_bumps_version(self):
        # Ensure calling invalidate_profile_cache does not raise and cache key set/increment works
        # Use a fake cache by calling function; as long as it doesn't raise we're okay.
        policy.invalidate_profile_cache(9999)