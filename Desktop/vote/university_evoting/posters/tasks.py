from evoting_system.celery import app
from .models import PosterSubmission
from .services import generate_poster_files
from audit.models import AuditLog
from django.utils import timezone
from .models import PosterAnalytics


@app.task(bind=True)
def generate_poster_task(self, submission_id):
    started = timezone.now()
    try:
        sub = PosterSubmission.objects.get(submission_id=submission_id)
        files = generate_poster_files(sub, template=sub.template)
        sub.generated_files = files
        sub.save()
        AuditLog.objects.create(user=sub.created_by, action='poster.generated', meta=str({'submission': str(sub.submission_id)}))
        duration = (timezone.now() - started).total_seconds()
        PosterAnalytics.objects.create(submission=sub, event='generated', duration_seconds=duration, details=files)
        return {'status': 'ok', 'files': files}
    except Exception as e:
        duration = (timezone.now() - started).total_seconds()
        PosterAnalytics.objects.create(submission_id=submission_id, event='generate_failed', duration_seconds=duration, details={'error': str(e)})
        AuditLog.objects.create(user=None, action='poster.generate_failed', meta=str({'submission': str(submission_id), 'error': str(e)}))
        raise
