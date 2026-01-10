from django.db import models


class Metric(models.Model):
    name = models.CharField(max_length=255)
    value = models.FloatField()
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} @ {self.recorded_at}: {self.value}"
