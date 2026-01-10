import hashlib
from . import crypto


def simple_encrypt_vote(candidate_id: int, token: str) -> str:
    """Prefer RSA public-key encryption if keys are present; otherwise fallback to SHA256 hash.
    Returns base64 ciphertext (RSA) or hex digest (fallback).
    """
    payload = f"{candidate_id}|{token}".encode("utf-8")
    try:
        # Use RSA public key encryption if available
        return crypto.encrypt_with_public(payload)
    except Exception:
        # Fallback to hash (non-reversible)
        return hashlib.sha256(payload).hexdigest()
