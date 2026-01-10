import tempfile
from pathlib import Path
from django.test import TestCase
from voting.key_provider import LocalFileKeyProvider, set_default_key_provider, get_default_key_provider
from voting import crypto


class KeyProviderTests(TestCase):
    def test_local_file_provider_key_generation_and_load(self):
        with tempfile.TemporaryDirectory() as d:
            provider = LocalFileKeyProvider(base_dir=Path(d))
            priv_path, pub_path = provider.generate_rsa_keypair(bits=2048)
            # ensure files exist
            assert Path(priv_path).exists()
            assert Path(pub_path).exists()
            # load via crypto helpers
            priv = crypto.load_private_key(priv_path)
            pub = crypto.load_public_key(pub_path)
            msg = b"hello"
            sig = priv.sign(msg, crypto.padding.PSS(mgf=crypto.padding.MGF1(crypto.hashes.SHA256()), salt_length=crypto.padding.PSS.MAX_LENGTH), crypto.hashes.SHA256())
            # verify with public key directly using cryptography API
            try:
                pub.verify(sig, msg, crypto.padding.PSS(mgf=crypto.padding.MGF1(crypto.hashes.SHA256()), salt_length=crypto.padding.PSS.MAX_LENGTH), crypto.hashes.SHA256())
            except Exception:
                assert False, "Signature verification with public key failed"

    def test_aws_kms_provider_unavailable_without_boto(self):
        # The AWSKMSKeyProvider will raise a RuntimeError when boto3 is missing; ensure the error is informative
        import importlib
        # emulate boto3 absence by temporarily removing from sys.modules
        import sys
        saved = sys.modules.pop('boto3', None)
        try:
            from voting.key_provider import AWSKMSKeyProvider
            try:
                AWSKMSKeyProvider(key_id='dummy')
                assert False, "Expected RuntimeError when boto3 not installed"
            except RuntimeError:
                pass
        finally:
            if saved is not None:
                sys.modules['boto3'] = saved
