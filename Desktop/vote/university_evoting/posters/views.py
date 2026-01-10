from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import PosterSubmission, PosterTemplate, ApprovedPoster
from .serializers import PosterSubmissionSerializer, PosterTemplateSerializer
from .services import compliance_check_submission
from audit.models import AuditLog
from .tasks import generate_poster_task
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class PosterSubmissionCreateView(generics.CreateAPIView):
    serializer_class = PosterSubmissionSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        # attach creating user
        serializer.save(created_by=self.request.user, candidate_user=self.request.user)

    def create(self, request, *args, **kwargs):
        resp = super().create(request, *args, **kwargs)
        submission_id = resp.data.get('submission_id')
        # perform compliance and kick off async generation
        try:
            sub = PosterSubmission.objects.get(submission_id=submission_id)
            errors = compliance_check_submission(sub.candidate_name, sub.slogan, sub.photo.path)
            if errors:
                AuditLog.objects.create(user=request.user, action='poster.submission_compliance_failed', meta=str(errors))
                return Response({'detail': 'submission failed compliance', 'errors': errors}, status=400)
            # enqueue background Celery task for generation
            try:
                generate_poster_task.delay(str(submission_id))
            except Exception:
                # fallback: try synchronous generation
                try:
                    from .services import generate_poster_files
                    files = generate_poster_files(sub, template=sub.template)
                    sub.generated_files = files
                    sub.save()
                    AuditLog.objects.create(user=sub.created_by, action='poster.generated', meta=str({'submission': str(sub.submission_id)}))
                except Exception:
                    AuditLog.objects.create(user=request.user, action='poster.generate_failed', meta=str({'submission': str(submission_id)}))
        except Exception:
            pass
        return resp



@method_decorator(login_required, name='dispatch')
class PosterSubmissionFormView(TemplateView):
    template_name = 'posters/submit.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['templates'] = PosterTemplate.objects.all()
        return ctx

    def post(self, request, *args, **kwargs):
        data = request.POST.dict()
        files = request.FILES
        serializer = PosterSubmissionSerializer(data={
            'candidate_user': request.user.id,
            'candidate_name': data.get('candidate_name'),
            'candidate_position': data.get('candidate_position'),
            'slogan': data.get('slogan'),
            'template': data.get('template') or None,
        }, files={'photo': files.get('photo')})
        if serializer.is_valid():
            obj = serializer.save(created_by=request.user, candidate_user=request.user)
            # enqueue generation
            try:
                generate_poster_task.delay(str(obj.submission_id))
            except Exception:
                pass
            # redirect to confirmation page for web UX
            from django.shortcuts import redirect
            from django.urls import reverse
            return redirect(reverse('poster-submit-confirm'))
        from django.shortcuts import render
        return render(request, self.template_name, {'templates': PosterTemplate.objects.all(), 'errors': serializer.errors})



class PosterModerationView(generics.RetrieveUpdateAPIView):
    queryset = PosterSubmission.objects.all()
    serializer_class = PosterSubmissionSerializer
    permission_classes = (IsAdminUser,)
    lookup_field = 'submission_id'

    def patch(self, request, *args, **kwargs):
        obj = self.get_object()
        action = request.data.get('action')
        reason = request.data.get('reason', '')
        if action == 'approve':
            obj.mark_approved(by_user=request.user, reason=reason)
            ApprovedPoster.objects.create(submission=obj)
            AuditLog.objects.create(user=request.user, action='poster.approved', meta=str({'submission': str(obj.submission_id)}))
            return Response({'detail': 'approved'})
        elif action == 'reject':
            obj.mark_rejected(by_user=request.user, reason=reason)
            AuditLog.objects.create(user=request.user, action='poster.rejected', meta=str({'submission': str(obj.submission_id), 'reason': reason}))
            return Response({'detail': 'rejected'})
        return Response({'detail': 'unknown action'}, status=status.HTTP_400_BAD_REQUEST)


class ModerationUI(TemplateView):
    template_name = 'posters/moderation.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['pending'] = PosterSubmission.objects.filter(status=PosterSubmission.STATUS_PENDING)
        return ctx


class PosterTemplatesListView(generics.ListAPIView):
    queryset = PosterTemplate.objects.all()
    serializer_class = PosterTemplateSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        # allow templates listing for form rendering
        return super().get(request, *args, **kwargs)


class ApprovedPostersGalleryView(generics.ListAPIView):
    serializer_class = PosterSubmissionSerializer
    permission_classes = ()

    def get_queryset(self):
        qs = PosterSubmission.objects.filter(status=PosterSubmission.STATUS_APPROVED)
        # randomize ordering for fairness
        return qs.order_by('?')


class PosterDownloadView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, submission_id, fmt='png'):
        sub = get_object_or_404(PosterSubmission, submission_id=submission_id, status=PosterSubmission.STATUS_APPROVED)
        files = sub.generated_files or {}
        path = files.get(fmt)
        if not path:
            return Response({'detail': 'file not available'}, status=404)
        from django.http import FileResponse
        return FileResponse(open(path, 'rb'), filename=f"poster_{submission_id}.{fmt}")
