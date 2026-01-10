from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.models import Profile
from abac.policy import evaluate


class ABACCacheTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="charlie", password="password")
        Profile.objects.create(user=self.user, role="student", status=Profile.STATUS_ACTIVE, attributes={"allowed_to_vote": True})

    def test_invalidate_on_profile_change(self):
        # initial decision should allow
        ok1 = evaluate(self.user, 'cast_vote')
        self.assertTrue(ok1)
        # change profile to disallow voting
        p = self.user.profile
        p.attributes['allowed_to_vote'] = False
        p.save()
        # re-evaluate and expect deny
        ok2 = evaluate(self.user, 'cast_vote')
        self.assertFalse(ok2)
