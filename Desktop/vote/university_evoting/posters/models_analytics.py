from django.db import models
from .models import PosterSubmission


class PosterAnalytics(models.Model):
    submission = models.ForeignKey(PosterSubmission, null=True, blank=True, on_delete=models.SET_NULL)
    event = models.CharField(max_length=100)
    duration_seconds = models.FloatField(null=True, blank=True)
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analytics {self.event} for {self.submission}"
