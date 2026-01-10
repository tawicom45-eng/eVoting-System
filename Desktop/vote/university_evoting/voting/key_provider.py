from __future__ import annotations
from pathlib import Path
import os
from typing import Optional, Tuple
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from django.conf import settings


class KeyProvider:
    """Abstract key provider interface. Implementations should provide ways to
    access vote and tally keys and optionally generate them."""

    def private_key_path(self) -> Optional[Path]:
        raise NotImplementedError

    def public_key_path(self) -> Optional[Path]:
        raise NotImplementedError

    def tally_private_key_path(self) -> Optional[Path]:
        raise NotImplementedError

    def tally_public_key_path(self) -> Optional[Path]:
        raise NotImplementedError

    def load_private_key(self, path: Optional[str | Path] = None):
        raise NotImplementedError

    def load_public_key(self, path: Optional[str | Path] = None):
        raise NotImplementedError

    def load_tally_private_key(self, path: Optional[str | Path] = None):
        raise NotImplementedError

    def load_tally_public_key(self, path: Optional[str | Path] = None):
        raise NotImplementedError

    def generate_rsa_keypair(self, bits: int = 2048, private_path: Optional[str | Path] = None, public_path: Optional[str | Path] = None) -> Tuple[str, str]:
        raise NotImplementedError


class LocalFileKeyProvider(KeyProvider):
    """Default local filesystem provider. Uses settings.VOTE_KEYS_DIR and
    settings.VOTE_PRIVATE_KEY_FILE / settings.VOTE_PUBLIC_KEY_FILE for vote keys
    and settings.TALLY_* for tally signing keys. Optionally can be constructed
    with explicit paths for testing."""

    def __init__(self, base_dir: Optional[str | Path] = None, vote_private: Optional[str] = None, vote_public: Optional[str] = None, tally_private: Optional[str] = None, tally_public: Optional[str] = None):
        self.base_dir = Path(base_dir) if base_dir else Path(getattr(settings, "VOTE_KEYS_DIR"))
        self.vote_private = vote_private or getattr(settings, "VOTE_PRIVATE_KEY_FILE")
        self.vote_public = vote_public or getattr(settings, "VOTE_PUBLIC_KEY_FILE")
        self.tally_private = tally_private or getattr(settings, "TALLY_PRIVATE_KEY_FILE")
        self.tally_public = tally_public or getattr(settings, "TALLY_PUBLIC_KEY_FILE")

    def _ensure_dir(self, path: Path):
        os.makedirs(path, exist_ok=True)

    def private_key_path(self) -> Path:
        return self.base_dir / self.vote_private

    def public_key_path(self) -> Path:
        return self.base_dir / self.vote_public

    def tally_private_key_path(self) -> Path:
        return self.base_dir / self.tally_private

    def tally_public_key_path(self) -> Path:
        return self.base_dir / self.tally_public

    def load_private_key(self, path: Optional[str | Path] = None):
        p = Path(path) if path else self.private_key_path()
        if not p.exists():
            return None
        data = p.read_bytes()
        return serialization.load_pem_private_key(data, password=None, backend=default_backend())

    def load_public_key(self, path: Optional[str | Path] = None):
        p = Path(path) if path else self.public_key_path()
        if not p.exists():
            return None
        data = p.read_bytes()
        return serialization.load_pem_public_key(data, backend=default_backend())

    def load_tally_private_key(self, path: Optional[str | Path] = None):
        p = Path(path) if path else self.tally_private_key_path()
        if not p.exists():
            return None
        data = p.read_bytes()
        return serialization.load_pem_private_key(data, password=None, backend=default_backend())

    def load_tally_public_key(self, path: Optional[str | Path] = None):
        p = Path(path) if path else self.tally_public_key_path()
        if not p.exists():
            return None
        data = p.read_bytes()
        return serialization.load_pem_public_key(data, backend=default_backend())

    def generate_rsa_keypair(self, bits: int = 2048, private_path: Optional[str | Path] = None, public_path: Optional[str | Path] = None) -> Tuple[str, str]:
        priv_path = Path(private_path) if private_path else self.private_key_path()
        pub_path = Path(public_path) if public_path else self.public_key_path()
        self._ensure_dir(priv_path.parent)

        private_key = rsa.generate_private_key(public_exponent=65537, key_size=bits, backend=default_backend())
        priv_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
        with open(priv_path, "wb") as f:
            f.write(priv_bytes)

        public_key = private_key.public_key()
        pub_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        with open(pub_path, "wb") as f:
            f.write(pub_bytes)

        return (str(priv_path), str(pub_path))


_default_provider: Optional[KeyProvider] = None


def get_default_key_provider() -> KeyProvider:
    global _default_provider
    if _default_provider is None:
        _default_provider = LocalFileKeyProvider()
    return _default_provider


def set_default_key_provider(provider: KeyProvider):
    global _default_provider
    _default_provider = provider


class AWSKMSKeyProvider(KeyProvider):
    """Minimal AWS KMS-backed key provider for asymmetric key signing (tally keys).

    This provider uses an AWS KMS asymmetric key for signing operations. It does not
    expose a raw private key; instead it returns a thin adapter with a .sign() method
    that delegates to KMS.Sign. This is intended for production usage where private
    keys must remain in KMS/HSM.
    """

    def __init__(self, key_id: str, region: str | None = None, boto3_session=None):
        # Prefer to detect presence of boto3 without re-importing (tests simulate absence by removing from sys.modules)
        import sys
        # If a boto3_session is explicitly provided (e.g., for tests), accept it even if boto3 isn't present in sys.modules.
        if boto3_session is None and 'boto3' not in sys.modules:
            raise RuntimeError("boto3 is required for AWSKMSKeyProvider")
        boto3 = sys.modules.get('boto3') if 'boto3' in sys.modules else None

        self.key_id = key_id
        self.region = region
        # create a session if not provided and boto3 available; do not create a client yet (lazy to avoid NoRegionError at init)
        self.session = boto3_session or (getattr(boto3, 'Session', None)() if boto3 is not None else None)
        self.client = None  # initialized lazily in methods that need it

    def private_key_path(self) -> None:
        return None

    def public_key_path(self) -> None:
        return None

    def tally_private_key_path(self) -> None:
        return None

    def tally_public_key_path(self) -> None:
        return None

    def load_private_key(self, path: Optional[str | Path] = None):
        return None

    def load_public_key(self, path: Optional[str | Path] = None):
        return None

    def load_tally_private_key(self, path: Optional[str | Path] = None):
        # Return an adapter with a .sign(message, *args, **kwargs) method that calls KMS.Sign
        # Accept 'path' forms like 'kms://<key_id>' or raw key id
        key_id = None
        if path:
            s = str(path)
            if s.startswith('kms://'):
                key_id = s.split('://', 1)[1]
            else:
                key_id = s
        else:
            key_id = getattr(self, 'key_id', None)

        class KMSPrivateKeyAdapter:
            def __init__(self, client, key_id):
                self.client = client
                self.key_id = key_id

            def sign(self, message, *args, **kwargs):
                # KMS.Sign expects bytes; use RSASSA_PSS_SHA_256 for RSA-PSS SHA256
                response = self.client.sign(KeyId=self.key_id, Message=message, SigningAlgorithm='RSASSA_PSS_SHA_256', MessageType='RAW')
                return response['Signature']

        # ensure client exists (may raise botocore.exceptions.NoRegionError if misconfigured)
        if self.client is None:
            self.client = self.session.client('kms', region_name=self.region)
        return KMSPrivateKeyAdapter(self.client, key_id)

    def load_tally_public_key(self, path: Optional[str | Path] = None):
        # Accept 'path' forms like 'kms://<key_id>' or raw key id
        key_id = None
        if path:
            s = str(path)
            if s.startswith('kms://'):
                key_id = s.split('://', 1)[1]
            else:
                key_id = s
        else:
            key_id = getattr(self, 'key_id', None)
        # KMS can return the public key via GetPublicKey; return PEM bytes
        # ensure client exists
        if self.client is None:
            self.client = self.session.client('kms', region_name=self.region)
        resp = self.client.get_public_key(KeyId=key_id)
        pub_bytes = resp.get('PublicKey')
        if pub_bytes is None:
            return None
        # cryptography can load DER-encoded public key bytes directly
        from cryptography.hazmat.primitives import serialization
        pub = serialization.load_der_public_key(pub_bytes, backend=default_backend())
        return pub

    def generate_rsa_keypair(self, bits: int = 2048, private_path: Optional[str | Path] = None, public_path: Optional[str | Path] = None) -> Tuple[str, str]:
        # Create an asymmetric key in KMS (RSA_2048 or RSA_4096)
        key_spec = 'RSA_2048' if bits == 2048 else 'RSA_4096'
        # ensure client exists
        if self.client is None:
            self.client = self.session.client('kms', region_name=self.region)
        resp = self.client.create_key(CustomerMasterKeySpec=key_spec, KeyUsage='SIGN_VERIFY', Origin='AWS_KMS')
        key_id = resp['KeyMetadata']['KeyId']
        # Return the key id as private and public path placeholders
        return (f"kms://{key_id}", f"kms://{key_id}")
