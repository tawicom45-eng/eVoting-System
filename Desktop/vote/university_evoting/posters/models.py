import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class PosterTemplate(models.Model):
    """Predefined poster templates."""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    background_image = models.ImageField(upload_to='posters/templates/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class PosterSubmission(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    submission_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    candidate_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    candidate_name = models.CharField(max_length=200)
    candidate_position = models.CharField(max_length=200)
    slogan = models.CharField(max_length=280, blank=True)
    photo = models.ImageField(upload_to='posters/photos/')
    template = models.ForeignKey(PosterTemplate, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    generated_files = models.JSONField(default=dict, blank=True)
    qr_code = models.ImageField(upload_to='posters/qrcodes/', null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='poster_submissions', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    moderated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='moderated_posters', null=True, blank=True, on_delete=models.SET_NULL)
    moderated_at = models.DateTimeField(null=True, blank=True)
    moderation_reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def mark_approved(self, by_user=None, reason=''):
        self.status = self.STATUS_APPROVED
        self.moderated_by = by_user
        self.moderated_at = timezone.now()
        self.moderation_reason = reason
        self.save()

    def mark_rejected(self, by_user=None, reason=''):
        self.status = self.STATUS_REJECTED
        self.moderated_by = by_user
        self.moderated_at = timezone.now()
        self.moderation_reason = reason
        self.save()

    def __str__(self):
        return f"PosterSubmission {self.submission_id} for {self.candidate_name} ({self.status})"


class ApprovedPoster(models.Model):
    submission = models.OneToOneField(PosterSubmission, on_delete=models.CASCADE, related_name='approved_poster')
    visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ApprovedPoster for {self.submission.candidate_name}"


class PosterAnalytics(models.Model):
    submission = models.ForeignKey(PosterSubmission, null=True, blank=True, on_delete=models.SET_NULL)
    event = models.CharField(max_length=100)
    duration_seconds = models.FloatField(null=True, blank=True)
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analytics {self.event} for {self.submission}"
