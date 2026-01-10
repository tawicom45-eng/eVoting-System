from django.db import models
from django.conf import settings
from elections.models import Election


class Complaint(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=50, default="open")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Complaint {self.id} - {self.subject} ({self.status})"
