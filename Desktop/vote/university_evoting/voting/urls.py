from django.urls import path
from .views import IssueTokenView, CastVoteView, QRCastView, QRLandingView, QRConfirmView, qr_success
from .views import QRIssueView, QRVerifyView

urlpatterns = [
    path("issue/<int:election_id>/", IssueTokenView.as_view(), name="api-issue-token"),
    path("cast/", CastVoteView.as_view(), name="api-cast-vote"),
    path("qr/<uuid:qr_slug>/", QRCastView.as_view(), name="api-qr-cast"),
    # public landing for QR scans (browser)
    path("qr/scan/<uuid:qr_slug>/", QRLandingView.as_view(), name="voting-qr-landing"),
    path("qr/api/issue/", QRIssueView.as_view(), name="api-qr-issue"),
    path("qr/api/verify/", QRVerifyView.as_view(), name="api-qr-verify"),
    path("qr/confirm/<uuid:qr_slug>/", QRConfirmView.as_view(), name="voting-qr-confirm"),
    path("qr/success/", qr_success, name='voting-qr-success'),
]
