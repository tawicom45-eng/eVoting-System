from django.db import models
from elections.models import Election


class LedgerEntry(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    entry_hash = models.CharField(max_length=256)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"LedgerEntry {self.election} @ {self.timestamp}"
