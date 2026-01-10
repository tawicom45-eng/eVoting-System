from django.db import models


class HealthCheck(models.Model):
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default="unknown")
    last_checked = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}: {self.status}"
