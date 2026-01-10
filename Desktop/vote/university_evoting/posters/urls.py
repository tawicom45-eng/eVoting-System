from django.urls import path
from .views import (
    PosterSubmissionCreateView,
    PosterModerationView,
    PosterTemplatesListView,
    ApprovedPostersGalleryView,
    PosterDownloadView,
    PosterSubmissionFormView,
)

urlpatterns = [
    # API endpoints
    path('submit/', PosterSubmissionCreateView.as_view(), name='poster-submit'),
    path('templates/', PosterTemplatesListView.as_view(), name='poster-templates'),
    path('moderate/<uuid:submission_id>/', PosterModerationView.as_view(), name='poster-moderate'),
    path('gallery/', ApprovedPostersGalleryView.as_view(), name='poster-gallery'),
    path('download/<uuid:submission_id>.<str:fmt>/', PosterDownloadView.as_view(), name='poster-download'),
    # Web form for candidates
    path('form/', PosterSubmissionFormView.as_view(), name='poster-submit-form'),
    path('form/confirm/', PosterSubmissionFormView.as_view(template_name='posters/submit_confirm.html'), name='poster-submit-confirm'),
]
