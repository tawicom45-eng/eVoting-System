from django.db import models
from django.conf import settings
from django.utils import timezone


class Report(models.Model):
    name = models.CharField(max_length=255)
    generated_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to="reports/", null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.generated_at})"


class ResultPublication(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_REVIEWED = 'reviewed'
    STATUS_PUBLISHED = 'published'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_REVIEWED, 'Reviewed'),
        (STATUS_PUBLISHED, 'Published'),
    ]

    election = models.ForeignKey('elections.Election', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    report = models.ForeignKey('reports.Report', null=True, blank=True, on_delete=models.SET_NULL)

    drafted_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='drafted_publications')
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='reviewed_publications')
    published_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='published_publications')

    reviewed_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    signature = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        permissions = [
            ('can_review_publication', 'Can mark publication as reviewed'),
            ('can_publish_publication', 'Can publish publication'),
        ]

    def __str__(self):
        return f"Publication for {self.election} - {self.status}"

    def mark_reviewed(self, user):
        from audit.models import AuditLog
        self.status = self.STATUS_REVIEWED
        self.reviewed_by = user
        self.reviewed_at = timezone.now()
        self.save()
        AuditLog.objects.create(user=user, action=f"Marked publication {self.pk} reviewed", meta=str({'election': self.election.pk}))

    def publish(self, user):
        from audit.models import AuditLog
        if self.status != self.STATUS_REVIEWED:
            raise ValueError("Publication must be reviewed before publishing")
        if self.reviewed_by_id == user.id:
            raise PermissionError("Reviewer cannot be publisher")
        self.status = self.STATUS_PUBLISHED
        self.published_by = user
        self.published_at = timezone.now()
        self.save()
        AuditLog.objects.create(user=user, action=f"Published results for publication {self.pk}", meta=str({'election': self.election.pk}))
