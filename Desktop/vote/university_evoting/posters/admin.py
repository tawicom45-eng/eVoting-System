from django.contrib import admin
from .models import PosterTemplate, PosterSubmission, ApprovedPoster


@admin.register(PosterTemplate)
class PosterTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')


@admin.register(PosterSubmission)
class PosterSubmissionAdmin(admin.ModelAdmin):
    list_display = ('submission_id', 'candidate_name', 'candidate_position', 'status', 'created_at')
    list_filter = ('status', 'candidate_position')
    readonly_fields = ('generated_files', 'qr_code')


@admin.register(ApprovedPoster)
class ApprovedPosterAdmin(admin.ModelAdmin):
    list_display = ('submission', 'visible', 'created_at')
