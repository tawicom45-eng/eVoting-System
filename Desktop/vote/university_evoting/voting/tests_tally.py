from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.management import call_command
from voting.crypto import generate_rsa_keypair
from elections.models import Election, Position, Candidate
from voting.models import EncryptedVote
import io


class TallyTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="voter1", password="pass")
        # ensure keys exist for encryption (written to project keys dir)
        self.priv, self.pub = generate_rsa_keypair()  # uses settings.VOTE_KEYS_DIR

        # Create an election with a position and candidates
        self.election = Election.objects.create(name="Tally Election", start_time="2025-01-01T00:00:00Z", end_time="2025-01-02T00:00:00Z", is_published=True)
        self.position = Position.objects.create(election=self.election, name="President")
        self.c1 = Candidate.objects.create(position=self.position, name="Alice", approved=True)
        self.c2 = Candidate.objects.create(position=self.position, name="Bob", approved=True)

        # Create encrypted votes: two for Alice, one for Bob
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import padding
        from cryptography.hazmat.primitives import hashes
        pub_data = open(self.pub, "rb").read()
        pubkey = serialization.load_pem_public_key(pub_data)

        def enc(candidate_id):
            pt = f"{candidate_id}|token-test".encode("utf-8")
            ct = pubkey.encrypt(pt, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
            import base64
            return base64.b64encode(ct).decode("utf-8")

        EncryptedVote.objects.create(election=self.election, position=self.position, candidate=self.c1, encrypted_payload=enc(self.c1.id))
        EncryptedVote.objects.create(election=self.election, position=self.position, candidate=self.c1, encrypted_payload=enc(self.c1.id))
        EncryptedVote.objects.create(election=self.election, position=self.position, candidate=self.c2, encrypted_payload=enc(self.c2.id))

    def test_tally_command_counts(self):
        # Run the management command to tally
        out = io.StringIO()
        call_command("tally_votes", str(self.election.id), stdout=out)
        output = out.getvalue()
        # The command prints a summary dict; check it contains total_counted=3
        self.assertIn("'total_counted': 3", output)
        # basic check: command succeeded and mentions "Tally complete"
        self.assertIn("Tally complete for election", output)
