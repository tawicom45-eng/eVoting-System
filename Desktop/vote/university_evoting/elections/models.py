from django.db import models
from django.conf import settings


class Election(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Position(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name="positions")
    name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.name} ({self.election.name})"


import uuid


class Candidate(models.Model):
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name="candidates")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200)
    manifesto = models.FileField(upload_to="manifestos/", null=True, blank=True)
    approved = models.BooleanField(default=False)

    # unique QR slug used to generate QR codes that link to casting endpoint
    qr_slug = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return f"{self.name} - {self.position.name}"

    def get_qr_endpoint(self):
        """Return the relative endpoint for QR-based casting."""
        return f"/api/voting/qr/{self.qr_slug}/"

    def get_absolute_qr_url(self, site_root: str):
        """Return an absolute URL for the QR which voters can scan."""
        return site_root.rstrip("/") + self.get_qr_endpoint()
