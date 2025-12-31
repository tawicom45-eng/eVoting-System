from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import ProfileSerializer

# Added simple auth endpoints for refresh-token rotation proof-of-concept
import base64
import os
import uuid
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password, check_password
from .models import AuthSession, RefreshToken, Profile
from audit.models import AuditLog
import logging

logger = logging.getLogger(__name__)


class MeView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        profile = getattr(request.user, "profile", None)
        if not profile:
            return Response({"detail": "Profile not found"}, status=404)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)


def generate_refresh_token_value():
    token_id = uuid.uuid4().hex
    secret = base64.urlsafe_b64encode(os.urandom(32)).decode("utf-8").rstrip("=")
    return f"{token_id}.{secret}", token_id, secret


class LoginView(APIView):
    def post(self, request):
        identifier = request.data.get("identifier")
        password = request.data.get("password")
        user = authenticate(request, username=identifier, password=password)
        if not user:
            return Response({"detail": "Invalid credentials"}, status=401)
        # Check profile status
        profile = getattr(user, "profile", None)
        if profile and profile.status != Profile.STATUS_ACTIVE:
            return Response({"detail": "User not active"}, status=403)
        # create session
        session = AuthSession.objects.create(user=user)
        token_value, token_id, secret = generate_refresh_token_value()
        token_hash = make_password(secret)
        RefreshToken.objects.create(session=session, token_id=token_id, token_hash=token_hash)
        access_token = f"access-{uuid.uuid4().hex}"
        return Response({"access_token": access_token, "refresh_token": token_value})


class RefreshView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response({"detail": "refresh_token required"}, status=400)
        try:
            token_id_str, secret = refresh_token.split(".")
        except Exception:
            return Response({"detail": "invalid token format"}, status=400)
        # locate token by id
        try:
            rid = uuid.UUID(token_id_str)
        except Exception:
            return Response({"detail": "invalid token id"}, status=400)
        candidates = RefreshToken.objects.filter(token_id=rid).order_by("-created_at")
        if not candidates.exists():
            return Response({"detail": "token not found"}, status=401)
        token = candidates.first()
        # If token already rotated, this may be reuse -> revoke session(s)
        if token.rotated:
            # token reuse detected
            # revoke all sessions for this user
            sess = token.session
            user = sess.user
            AuthSession.objects.filter(user=user, revoked=False).update(revoked=True)
            # audit
            ip = request.META.get('REMOTE_ADDR')
            AuditLog.objects.create(user=user, action="refresh_token_reuse_detected", ip_address=ip, meta=f"token_id={token.token_id}")
            logger.warning("Refresh token reuse detected", extra={"user_id": user.id, "token_id": str(token.token_id)})
            return Response({"detail": "token reuse detected; sessions revoked"}, status=401)
        # Ensure session not revoked already
        if token.session.revoked:
            return Response({"detail": "session revoked"}, status=401)
        if not check_password(secret, token.token_hash):
            # possible token misuse: revoke session
            AuthSession.objects.filter(id=token.session.id, revoked=False).update(revoked=True)
            ip = request.META.get('REMOTE_ADDR')
            AuditLog.objects.create(user=token.session.user, action="invalid_refresh_token", ip_address=ip, meta=f"token_id={token.token_id}")
            logger.warning("Invalid refresh token used", extra={"user_id": token.session.user.id, "token_id": str(token.token_id)})
            return Response({"detail": "invalid token"}, status=401)
        # rotate token: mark old as rotated and create a new token for same session
        token.rotated = True
        token.save()
        new_token_value, new_token_id, new_secret = generate_refresh_token_value()
        new_token_hash = make_password(new_secret)
        RefreshToken.objects.create(session=token.session, token_id=new_token_id, token_hash=new_token_hash)
        access_token = f"access-{uuid.uuid4().hex}"
        return Response({"access_token": access_token, "refresh_token": new_token_value})


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        # Revoke all sessions for current user
        AuthSession.objects.filter(user=request.user, revoked=False).update(revoked=True)
        return Response({"detail": "logged out"})
