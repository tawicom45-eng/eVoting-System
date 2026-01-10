import tempfile
from pathlib import Path
from django.test import TestCase
from voting.key_provider import LocalFileKeyProvider
from cryptography.hazmat.primitives import hashes


class KeyProviderTests(TestCase):
    def test_local_file_provider_generate_and_load(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            provider = LocalFileKeyProvider(base_dir=base, vote_private="priv.pem", vote_public="pub.pem", tally_private="tpriv.pem", tally_public="tpub.pem")

            priv_path, pub_path = provider.generate_rsa_keypair(bits=1024)
            self.assertTrue(Path(priv_path).exists())
            self.assertTrue(Path(pub_path).exists())

            pub = provider.load_public_key()
            priv = provider.load_private_key()
            self.assertIsNotNone(pub)
            self.assertIsNotNone(priv)

            # quick encrypt/decrypt roundtrip
            plaintext = b"hello"
            ciphertext = pub.encrypt(
                plaintext,
                priv._backend._lib.Cryptography_RSA_padding_oaep # not used; fallback using public_key.encrypt below
            ) if False else pub.encrypt(
                plaintext,
                padding=__import__('cryptography.hazmat.primitives.asymmetric.padding', fromlist=['OAEP']).OAEP(mgf=__import__('cryptography.hazmat.primitives.asymmetric.padding', fromlist=['MGF1']).MGF1(hashes.SHA256()), algorithm=__import__('cryptography.hazmat.primitives.hashes', fromlist=['SHA256']).SHA256(), label=None)
            )
            pt = priv.decrypt(
                ciphertext,
                __import__('cryptography.hazmat.primitives.asymmetric.padding', fromlist=['OAEP']).OAEP(mgf=__import__('cryptography.hazmat.primitives.asymmetric.padding', fromlist=['MGF1']).MGF1(hashes.SHA256()), algorithm=__import__('cryptography.hazmat.primitives.hashes', fromlist=['SHA256']).SHA256(), label=None)
            )
            self.assertEqual(pt, plaintext)

    def test_tally_keys_generate_and_load(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            provider = LocalFileKeyProvider(base_dir=base, vote_private="p.pem", vote_public="q.pem", tally_private="tpriv.pem", tally_public="tpub.pem")
            tpriv, tpub = provider.generate_rsa_keypair(bits=1024, private_path=provider.tally_private_key_path(), public_path=provider.tally_public_key_path())
            self.assertTrue(Path(tpriv).exists())
            self.assertTrue(Path(tpub).exists())
            self.assertIsNotNone(provider.load_tally_private_key())
            self.assertIsNotNone(provider.load_tally_public_key())
