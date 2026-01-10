import uuid
from django.db import models
from django.conf import settings
from elections.models import Election, Position, Candidate


class VoteToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    used = models.BooleanField(default=False)

    def __str__(self):
        return f"Token {self.token} for {self.user} ({'used' if self.used else 'unused'})"


class EncryptedVote(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    encrypted_payload = models.TextField()
    # Base64 signature of encrypted_payload signed by tally private key (PSS + SHA256)
    signature = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"EncryptedVote {self.id} - {self.election.name}"


class QRTokenUsage(models.Model):
    """Records used signed QR tokens to prevent replay."""
    token_hash = models.CharField(max_length=128, unique=True)
    used_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    candidate = models.ForeignKey(Candidate, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"QRTokenUsage {self.token_hash} -> {self.used_at}"


class QRLink(models.Model):
    """Issued per-user signed QR link with TTL and usage state."""
    token = models.CharField(max_length=512, unique=True)
    token_hash = models.CharField(max_length=128, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    used = models.BooleanField(default=False)

    def is_valid(self):
        from django.utils import timezone
        if self.used:
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        return True

    def mark_used(self):
        self.used = True
        self.save()

    def __str__(self):
        return f"QRLink token_hash={self.token_hash} user={self.user} candidate={self.candidate}"
