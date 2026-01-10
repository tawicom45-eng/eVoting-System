from django.test import TestCase
from voting.crypto import generate_rsa_keypair, sign_with_tally_private, verify_with_tally_public


class SignatureTests(TestCase):
    def test_sign_and_verify(self):
        # generate tally keys in project keys dir
        generate_rsa_keypair(private_path=None, public_path=None)
        from voting.crypto import tally_private_key_path, tally_public_key_path
        # generate tally signing keys explicitly
        generate_rsa_keypair(private_path=tally_private_key_path(), public_path=tally_public_key_path())

        msg = b"sample-payload"
        sig = sign_with_tally_private(msg)
        ok = verify_with_tally_public(msg, sig)
        self.assertTrue(ok)

    def test_invalid_signature_detected(self):
        generate_rsa_keypair(private_path=None, public_path=None)
        from voting.crypto import tally_private_key_path, tally_public_key_path
        generate_rsa_keypair(private_path=tally_private_key_path(), public_path=tally_public_key_path())

        msg = b"sample-payload"
        sig = sign_with_tally_private(msg)
        self.assertFalse(verify_with_tally_public(b"tampered", sig))
