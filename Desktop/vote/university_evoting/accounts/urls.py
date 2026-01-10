from django.urls import path
from .views import (
    MeView,
    MFATOTPRegisterView,
    MFATOTPVerifyView,
    MFATOTPListView,
    MFATOTPDeleteView,
    MagicLinkRequestView,
    MagicLinkVerifyView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    LoginView,
    RefreshView,
    LogoutView,
    QRIssueLoginView,
    QRLoginVerifyView,
    TrustedDeviceListCreateView,
    TrustedDeviceDeleteView,
)

urlpatterns = [
    path("me/", MeView.as_view(), name="api-me"),
    # MFA (TOTP)
    path("mfa/totp/register/", MFATOTPRegisterView.as_view(), name="mfa-totp-register"),
    path("mfa/totp/verify/", MFATOTPVerifyView.as_view(), name="mfa-totp-verify"),
    path("mfa/totp/", MFATOTPListView.as_view(), name="mfa-totp-list"),
    path("mfa/totp/<int:pk>/", MFATOTPDeleteView.as_view(), name="mfa-totp-delete"),
    # Magic link (passwordless)
    path("magic/request/", MagicLinkRequestView.as_view(), name="magic-request"),
    path("magic/verify/", MagicLinkVerifyView.as_view(), name="magic-verify"),
    # Password reset
    path("password/reset/request/", PasswordResetRequestView.as_view(), name='password-reset-request'),
    path("password/reset/confirm/", PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    # Auth core
    path("login/", LoginView.as_view(), name="login"),
    path("token/refresh/", RefreshView.as_view(), name="token-refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    # QR login (admin issue + verify)
    path("qr/login/issue/", QRIssueLoginView.as_view(), name='qr-login-issue'),
    path("qr/login/verify/", QRLoginVerifyView.as_view(), name='qr-login-verify'),
    # Trusted device registry
    path("devices/", TrustedDeviceListCreateView.as_view(), name='trusted-devices-list'),
    path("devices/<uuid:device_id>/", TrustedDeviceDeleteView.as_view(), name='trusted-devices-delete'),
]
