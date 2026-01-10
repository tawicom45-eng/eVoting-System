from django.db import models
from elections.models import Election


class VerificationRecord(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    verified = models.BooleanField(default=False)
    report_hash = models.CharField(max_length=256, blank=True)
    checked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Verification {self.election} - {self.verified}"
