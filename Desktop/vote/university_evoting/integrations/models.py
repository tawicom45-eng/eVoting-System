from django.db import models


class ExternalIntegration(models.Model):
    name = models.CharField(max_length=255)
    config = models.JSONField(default=dict, blank=True)
    enabled = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({'enabled' if self.enabled else 'disabled'})"
