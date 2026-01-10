from django.test import TestCase
import boto3
import moto
from voting.key_provider import AWSKMSKeyProvider
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes


@moto.mock_aws
class KMSProviderMotoTest(TestCase):
    def test_kms_provider_with_moto(self):
        # create a client in the mocked environment
        session = boto3.session.Session()
        client = session.client('kms', region_name='us-east-1')
        # create an asymmetric RSA key in moto
        resp = client.create_key(CustomerMasterKeySpec='RSA_2048', KeyUsage='SIGN_VERIFY', Origin='AWS_KMS')
        key_id = resp['KeyMetadata']['KeyId']
        # initialize provider with the same session
        provider = AWSKMSKeyProvider(key_id=key_id, region='us-east-1', boto3_session=session)
        # load public key and sign adapter
        pub = provider.load_tally_public_key(key_id)
        self.assertIsNotNone(pub)
        adapter = provider.load_tally_private_key(key_id)
        msg = b'test message'
        sig = adapter.sign(msg)
        # verify signature using loaded public key
        pub.verify(sig, msg, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
