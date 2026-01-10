from django.test import TestCase, Client
from django.contrib.auth import get_user_model


class SingleSessionTests(TestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='single', password='pass')

    def test_only_one_active_session(self):
        c1 = Client()
        c2 = Client()

        self.assertTrue(c1.login(username='single', password='pass'))
        # c1 should have session
        s1_key = c1.session.session_key
        self.assertIsNotNone(s1_key)

        # login from second client; this should kill the first client's session
        self.assertTrue(c2.login(username='single', password='pass'))
        s2_key = c2.session.session_key
        self.assertIsNotNone(s2_key)
        self.assertNotEqual(s1_key, s2_key)

        # first client should now be logged out (session no longer valid)
        res = c1.get('/api/voting/qr/success/')
        # expect redirect to login or 200 depending on view, but session should not be authenticated
        # check that accessing a login-required view results in non-authenticated state
        # We assert that the session no longer contains the auth key
        self.assertNotIn('_auth_user_id', c1.session)
