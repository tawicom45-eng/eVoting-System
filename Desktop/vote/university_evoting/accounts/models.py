import uuid
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=64, blank=True, null=True, unique=True)
    ROLE_CHOICES = [
        ("student", "Student"),
        ("staff", "Staff"),
        ("admin", "Admin"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="student")

    STATUS_ACTIVE = 'active'
    STATUS_SUSPENDED = 'suspended'
    STATUS_ARCHIVED = 'archived'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_SUSPENDED, 'Suspended'),
        (STATUS_ARCHIVED, 'Archived'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)

    campus = models.CharField(max_length=100, blank=True)
    faculty = models.CharField(max_length=100, blank=True)

    # Generic attributes for ABAC and integrations
    attributes = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


# Authentication session and refresh token models
class AuthSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    session_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    device = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    revoked = models.BooleanField(default=False)

    def __str__(self):
        return f"Session {self.session_id} for {self.user} ({'revoked' if self.revoked else 'active'})"


class RefreshToken(models.Model):
    session = models.ForeignKey(AuthSession, on_delete=models.CASCADE, related_name="refresh_tokens")
    token_id = models.UUIDField(default=uuid.uuid4, editable=False)
    token_hash = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)
    rotated = models.BooleanField(default=False)

    class Meta:
        indexes = [models.Index(fields=["token_id"]) ]

    def __str__(self):
        return f"RefreshToken {self.token_id} (rotated={self.rotated})"


class RevokedAccessToken(models.Model):
    """Tracks issued access tokens and their revocation state (simple JTI revocation list).

    This is intentionally simple for the POC: store a UUID JTI, link to an auth session and allow
    marking revoked when refresh-token misuse is detected.
    """
    jti = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    session = models.ForeignKey(AuthSession, on_delete=models.CASCADE, related_name="access_tokens")
    issued_at = models.DateTimeField(auto_now_add=True)
    revoked = models.BooleanField(default=False)
    revoked_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"AccessToken {self.jti} (revoked={self.revoked})"


# MFA devices (TOTP + WebAuthn)
class MFATOTPDevice(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="totp_devices")
    label = models.CharField(max_length=100, blank=True)
    secret = models.CharField(max_length=256)  # encrypted token (Fernet) stored as text
    confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"TOTP device {self.label} for {self.user} (confirmed={self.confirmed})"

    @property
    def plaintext_secret(self):
        """Return decrypted secret (plaintext base32) or None if decryption fails."""
        try:
            from .crypto import decrypt_secret
            return decrypt_secret(self.secret)
        except Exception:
            return None

    def save(self, *args, **kwargs):
        # Ensure the secret is stored encrypted. If it already decrypts with configured keys,
        # leave it as-is. Otherwise assume it's plaintext and encrypt with the current key.
        from .crypto import encrypt_secret, decrypt_secret
        if self.secret:
            needs_encrypt = False
            try:
                # If decrypt succeeds, it is already encrypted with a known key
                _ = decrypt_secret(self.secret)
            except Exception:
                needs_encrypt = True
            if needs_encrypt:
                try:
                    self.secret = encrypt_secret(self.secret)
                except Exception:
                    # If encryption fails, raise to avoid saving plaintext silently
                    raise
        super().save(*args, **kwargs)


class WebAuthnCredential(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="webauthn_credentials")
    credential_id = models.BinaryField()
    public_key = models.TextField()
    sign_count = models.IntegerField(default=0)
    label = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"WebAuthn credential {self.label} for {self.user}"


class QRLoginToken(models.Model):
    """Admin-issued signed QR tokens for passwordless login (one-time use)."""
    token = models.TextField()
    token_hash = models.CharField(max_length=128, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='qr_login_tokens')
    issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='issued_qr_login_tokens')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    used = models.BooleanField(default=False)

    def __str__(self):
        return f"QRLoginToken for {self.user} (used={self.used})"


# Hook profile changes to invalidate ABAC cache versioning
from django.db.models.signals import post_save
from django.dispatch import receiver
from abac import policy as abac_policy

@receiver(post_save, sender=Profile)
def _invalidate_abac_on_profile_change(sender, instance, **kwargs):
    try:
        abac_policy.invalidate_profile_cache(instance.user.id)
    except Exception:
        # Non-critical; don't fail saves on cache problems
        pass
