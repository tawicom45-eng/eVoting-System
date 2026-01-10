from django.db import models
from elections.models import Election


class OfflineBatch(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    data_blob = models.BinaryField()
    imported = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OfflineBatch {self.id} ({'imported' if self.imported else 'pending'})"
