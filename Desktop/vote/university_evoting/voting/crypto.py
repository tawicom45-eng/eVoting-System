import base64
import os
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from django.conf import settings


from .key_provider import get_default_key_provider


def keys_dir() -> Path:
    provider = get_default_key_provider()
    # provider may expose a base_dir attribute
    base = getattr(provider, "base_dir", None)
    if base:
        return Path(base)
    return Path(settings.VOTE_KEYS_DIR)


def private_key_path() -> Path:
    provider = get_default_key_provider()
    path = provider.private_key_path()
    return Path(path) if path else Path(settings.VOTE_KEYS_DIR) / settings.VOTE_PRIVATE_KEY_FILE


def public_key_path() -> Path:
    provider = get_default_key_provider()
    path = provider.public_key_path()
    return Path(path) if path else Path(settings.VOTE_KEYS_DIR) / settings.VOTE_PUBLIC_KEY_FILE


def generate_rsa_keypair(bits: int = 2048, private_path: str | Path | None = None, public_path: str | Path | None = None):
    provider = get_default_key_provider()
    return provider.generate_rsa_keypair(bits=bits, private_path=private_path, public_path=public_path)


def load_public_key(path: str | Path | None = None):
    provider = get_default_key_provider()
    return provider.load_public_key(path=path)


def load_private_key(path: str | Path | None = None):
    provider = get_default_key_provider()
    return provider.load_private_key(path=path)


def encrypt_with_public(plaintext: bytes) -> str:
    pub = load_public_key()
    if not pub:
        raise RuntimeError("Public key not found; generate keys with management command")
    ct = pub.encrypt(
        plaintext,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None),
    )
    return base64.b64encode(ct).decode("utf-8")


def decrypt_with_private(ciphertext_b64: str) -> bytes:
    priv = load_private_key()
    if not priv:
        raise RuntimeError("Private key not found; generate keys with management command")
    ct = base64.b64decode(ciphertext_b64.encode("utf-8"))
    pt = priv.decrypt(ct, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
    return pt


# Signing helper utilities (use tally keys)

def tally_private_key_path() -> Path:
    provider = get_default_key_provider()
    path = provider.tally_private_key_path()
    return Path(path) if path else Path(settings.VOTE_KEYS_DIR) / settings.TALLY_PRIVATE_KEY_FILE


def tally_public_key_path() -> Path:
    provider = get_default_key_provider()
    path = provider.tally_public_key_path()
    return Path(path) if path else Path(settings.VOTE_KEYS_DIR) / settings.TALLY_PUBLIC_KEY_FILE


def load_tally_private_key(path: str | Path | None = None):
    provider = get_default_key_provider()
    return provider.load_tally_private_key(path=path)


def load_tally_public_key(path: str | Path | None = None):
    provider = get_default_key_provider()
    return provider.load_tally_public_key(path=path)


def sign_with_tally_private(message: bytes) -> str:
    priv = load_tally_private_key()
    if not priv:
        raise RuntimeError("Tally signing private key not found; generate with management command")
    sig = priv.sign(
        message,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256(),
    )
    return base64.b64encode(sig).decode("utf-8")


def verify_with_tally_public(message: bytes, signature_b64: str) -> bool:
    pub = load_tally_public_key()
    if not pub:
        raise RuntimeError("Tally signing public key not found; generate with management command")
    sig = base64.b64decode(signature_b64.encode("utf-8"))
    try:
        pub.verify(
            sig,
            message,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256(),
        )
        return True
    except Exception:
        return False

