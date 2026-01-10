from django.test import TestCase
from voting.key_provider import AWSKMSKeyProvider
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa


class FakeKMSClient:
    def __init__(self):
        self.keys = {}

    def create_key(self, CustomerMasterKeySpec=None, KeyUsage=None, Origin=None):
        # Generate RSA keypair
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        key_id = f"fake-key-{len(self.keys)+1}"
        self.keys[key_id] = private_key
        return {'KeyMetadata': {'KeyId': key_id}}

    def get_public_key(self, KeyId=None):
        priv = self.keys.get(KeyId)
        if not priv:
            raise ValueError('Key not found')
        pub = priv.public_key().public_bytes(encoding=serialization.Encoding.DER, format=serialization.PublicFormat.SubjectPublicKeyInfo)
        return {'PublicKey': pub}

    def sign(self, KeyId=None, Message=None, SigningAlgorithm=None, MessageType=None):
        priv = self.keys.get(KeyId)
        if not priv:
            raise ValueError('Key not found')
        sig = priv.sign(Message, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
        return {'Signature': sig}


class FakeSession:
    def __init__(self, client):
        self._client = client

    def client(self, service_name, region_name=None):
        if service_name == 'kms':
            return self._client
        raise RuntimeError('Unsupported service')


class KMSProviderE2ETest(TestCase):
    def test_kms_provider_create_and_sign(self):
        fake_client = FakeKMSClient()
        session = FakeSession(fake_client)
        provider = AWSKMSKeyProvider(key_id='unused', boto3_session=session)
        # create a key
        priv_uri, pub_uri = provider.generate_rsa_keypair(bits=2048)
        assert priv_uri.startswith('kms://')
        key_id = priv_uri.split('://', 1)[1]
        # load public key via provider
        pub = provider.load_tally_public_key(key_id)
        assert pub is not None
        # load private adapter and sign
        adapter = provider.load_tally_private_key(key_id)
        message = b'hello'
        sig = adapter.sign(message)
        # verify signature using loaded public key
        pub.verify(sig, message, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
