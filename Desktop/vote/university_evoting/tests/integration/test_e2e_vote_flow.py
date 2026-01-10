from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from elections.models import Election, Position, Candidate
from voting.models import VoteToken, EncryptedVote


class EndToEndVoteFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.user = User.objects.create_user(username="voter1", password="testpass")
        # Ensure Profile exists for the user
        from accounts.models import Profile
        Profile.objects.create(user=self.user, role="student", status=Profile.STATUS_ACTIVE)

        # Create sample election window that includes now
        now = timezone.now()
        self.election = Election.objects.create(
            name="Test Election",
            start_time=now - timezone.timedelta(hours=1),
            end_time=now + timezone.timedelta(hours=1),
            is_published=True,
        )
        self.position = Position.objects.create(election=self.election, name="President")
        self.candidate = Candidate.objects.create(position=self.position, name="Alice", approved=True)

    def test_issue_token_and_cast_vote(self):
        # Authenticate and issue token
        self.client.force_authenticate(user=self.user)
        resp = self.client.post(f"/api/voting/issue/{self.election.id}/")
        self.assertEqual(resp.status_code, 200)
        token = resp.data.get("token")
        self.assertIsNotNone(token)

        # Cast vote
        payload = {"token": token, "position_id": self.position.id, "candidate_id": self.candidate.id}
        cast_resp = self.client.post("/api/voting/cast/", payload, format="json")
        self.assertEqual(cast_resp.status_code, 201)

        # Check token used flag#
        vt = VoteToken.objects.get(token=token)
        self.assertTrue(vt.used)

        # Check EncryptedVote created
        ev = EncryptedVote.objects.filter(election=self.election, position=self.position, candidate=self.candidate).first()
        self.assertIsNotNone(ev)
        # Encrypted payload should exist and be non-empty
        self.assertTrue(ev.encrypted_payload and len(ev.encrypted_payload) > 10)

    def test_token_reuse_is_rejected(self):
        self.client.login(username="voter1", password="testpass")
        resp = self.client.post(f"/api/voting/issue/{self.election.id}/")
        token = resp.data.get("token")
        payload = {"token": token, "position_id": self.position.id, "candidate_id": self.candidate.id}
        r1 = self.client.post("/api/voting/cast/", payload, format="json")
        self.assertEqual(r1.status_code, 201)
        r2 = self.client.post("/api/voting/cast/", payload, format="json")
        self.assertEqual(r2.status_code, 400)

    def test_token_belongs_to_user(self):
        # Issue token as user1
        self.client.force_authenticate(user=self.user)
        resp = self.client.post(f"/api/voting/issue/{self.election.id}/")
        token = resp.data.get("token")
        self.client.force_authenticate(user=None)

        # Create another user and try to use the token
        User = get_user_model()
        other = User.objects.create_user(username="other", password="pass")
        # ensure a Profile exists so ABAC policy evaluation can make a decision
        from accounts.models import Profile
        Profile.objects.create(user=other, role="student", status=Profile.STATUS_ACTIVE)
        self.client.force_authenticate(user=other)
        payload = {"token": token, "position_id": self.position.id, "candidate_id": self.candidate.id}
        r = self.client.post("/api/voting/cast/", payload, format="json")
        # Should 404 because token not found for this user
        self.assertEqual(r.status_code, 404)

    def test_suspended_user_cannot_issue_or_cast(self):
        # Suspend user
        profile = getattr(self.user, "profile", None)
        if profile:
            profile.status = "suspended"
            profile.save()

        self.client.force_authenticate(user=self.user)
        r1 = self.client.post(f"/api/voting/issue/{self.election.id}/")
        self.assertEqual(r1.status_code, 403)

        # Create token bypassing API to simulate a leaked token and ensure cast is rejected
        from voting.models import VoteToken
        vt = VoteToken.objects.create(user=self.user, election=self.election)
        payload = {"token": str(vt.token), "position_id": self.position.id, "candidate_id": self.candidate.id}
        r2 = self.client.post("/api/voting/cast/", payload, format="json")
        self.assertEqual(r2.status_code, 403)

    def test_abac_denies_based_on_profile_attribute(self):
        profile = getattr(self.user, "profile", None)
        profile.attributes["allowed_to_vote"] = False
        profile.save()

        self.client.login(username="voter1", password="testpass")
        r = self.client.post(f"/api/voting/issue/{self.election.id}/")
        self.assertEqual(r.status_code, 403)
 # self-authentication needed