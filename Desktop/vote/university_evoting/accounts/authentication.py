import hmac
import hashlib
import uuid
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from django.conf import settings
from .models import RevokedAccessToken


import logging
logger = logging.getLogger(__name__)

def _verify_signature(jti_str, signature):
    secret = getattr(settings, "ACCESS_TOKEN_SECRET", None)
    if not secret:
        raise exceptions.AuthenticationFailed("access token signing key not configured")
    mac = hmac.new(secret.encode("utf-8"), jti_str.encode("utf-8"), hashlib.sha256).hexdigest()
    # constant time compare
    if not hmac.compare_digest(mac, signature):
        logger.debug("Invalid access token signature for jti %s", jti_str)
        return False
    return True


class JTIAuthentication(BaseAuthentication):
    """Authenticate using access token format: <jti>.<signature>

    The signature is HMAC-SHA256 over the JTI using ACCESS_TOKEN_SECRET.
    The token's JTI must not be in RevokedAccessToken.revoked == True.
    On success, returns (user, token) where token is the jti string.
    """

    def authenticate(self, request):
        auth = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth or not auth.startswith("Bearer "):
            return None
        token = auth.split(" ", 1)[1]
        parts = token.split(".")
        if len(parts) != 2:
            raise exceptions.AuthenticationFailed("invalid token format")
        jti_str, signature = parts
        try:
            jti = uuid.UUID(jti_str)
        except Exception:
            # malformed jti — treat as unauthenticated so permission checks will return 401
            return None
        # verify signature
        if not _verify_signature(jti_str, signature):
            # invalid signature — treat as unauthenticated
            return None
        # ensure not revoked
        try:
            revoked = RevokedAccessToken.objects.filter(jti=jti, revoked=True).exists()
        except Exception:
            # DB error -> fail closed (treat as unauthenticated)
            return None
        if revoked:
            # revoked token — treat as unauthenticated
            return None
        # return associated user
        token_obj = RevokedAccessToken.objects.filter(jti=jti).first()
        if not token_obj:
            # token not in DB — treat as unauthenticated
            return None
        user = token_obj.session.user
        return (user, token)
