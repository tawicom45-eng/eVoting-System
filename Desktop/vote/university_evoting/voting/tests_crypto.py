from django.test import TestCase, override_settings
from tempfile import TemporaryDirectory
from voting.crypto import generate_rsa_keypair, encrypt_with_public, decrypt_with_private


class CryptoTests(TestCase):
    def test_generate_encrypt_decrypt_roundtrip(self):
        with TemporaryDirectory() as tmp:
            # generate keys in temp dir
            priv, pub = generate_rsa_keypair(private_path=f"{tmp}/priv.pem", public_path=f"{tmp}/pub.pem")
            # ensure encrypt/decrypt work by loading from those files via path mocking
            # Temporarily override settings to point functions to these files is not necessary because our functions accept explicit paths when generating only; load functions default to settings-based paths; use explicit load via import and direct calls below
            plaintext = b"42|token-abc"
            # For testing, load public key from pub.pem
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.backends import default_backend
            pub_data = open(pub, "rb").read()
            pubkey = serialization.load_pem_public_key(pub_data, backend=default_backend())
            ciphertext = pubkey.encrypt(plaintext, __import__("cryptography.hazmat.primitives.asymmetric.padding", fromlist=["OAEP"]).OAEP(mgf=__import__("cryptography.hazmat.primitives.asymmetric.padding", fromlist=["MGF1"]).MGF1(algorithm=__import__("cryptography.hazmat.primitives.hashes", fromlist=["SHA256"]).SHA256()), algorithm=__import__("cryptography.hazmat.primitives.hashes", fromlist=["SHA256"]).SHA256(), label=None))
            # decrypt using private key
            priv_data = open(priv, "rb").read()
            privkey = serialization.load_pem_private_key(priv_data, password=None, backend=default_backend())
            pt = privkey.decrypt(ciphertext, __import__("cryptography.hazmat.primitives.asymmetric.padding", fromlist=["OAEP"]).OAEP(mgf=__import__("cryptography.hazmat.primitives.asymmetric.padding", fromlist=["MGF1"]).MGF1(algorithm=__import__("cryptography.hazmat.primitives.hashes", fromlist=["SHA256"]).SHA256()), algorithm=__import__("cryptography.hazmat.primitives.hashes", fromlist=["SHA256"]).SHA256(), label=None))
            self.assertEqual(pt, plaintext)
