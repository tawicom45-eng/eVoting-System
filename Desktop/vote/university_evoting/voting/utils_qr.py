import hashlib
from django.core import signing
from django.conf import settings
from typing import Optional
from datetime import timedelta
import time

SIGNED_QR_SALT = getattr(settings, 'SIGNED_QR_SALT', 'voting-signed-qr')
SIGNED_QR_MAX_AGE = getattr(settings, 'SIGNED_QR_MAX_AGE', 300)  # seconds


def generate_signed_qr_token(user_id: int, candidate_id: int) -> str:
    payload = {'u': int(user_id), 'c': int(candidate_id), 'ts': int(time.time())}
    return signing.dumps(payload, salt=SIGNED_QR_SALT)


def verify_signed_qr_token(token: str, max_age: Optional[int] = None) -> dict:
    max_age = max_age or SIGNED_QR_MAX_AGE
    try:
        data = signing.loads(token, salt=SIGNED_QR_SALT, max_age=max_age)
        return data
    except signing.SignatureExpired:
        raise
    except signing.BadSignature:
        raise


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode('utf-8')).hexdigest()
