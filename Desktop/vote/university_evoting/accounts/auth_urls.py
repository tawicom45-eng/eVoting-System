from django.urls import path
from .views import (
    LoginView,
    RefreshView,
    LogoutView,
    MFATOTPRegisterView,
    MFATOTPVerifyView,
    MFATOTPListView,
    MFATOTPDeleteView,
    WebAuthnRegisterOptionsView,
    WebAuthnRegisterCompleteView,
    WebAuthnAuthOptionsView,
    WebAuthnAuthCompleteView,
)

urlpatterns = [
    path("login/", LoginView.as_view(), name="api-auth-login"),
    path("refresh/", RefreshView.as_view(), name="api-auth-refresh"),
    path("logout/", LogoutView.as_view(), name="api-auth-logout"),
    # MFA (TOTP)
    path("mfa/totp/register/", MFATOTPRegisterView.as_view(), name="mfa-totp-register"),
    path("mfa/totp/verify/", MFATOTPVerifyView.as_view(), name="mfa-totp-verify"),
    path("mfa/totp/", MFATOTPListView.as_view(), name="mfa-totp-list"),
    path("mfa/totp/<int:pk>/", MFATOTPDeleteView.as_view(), name="mfa-totp-delete"),
    # WebAuthn (passkeys)
    path("webauthn/register/options/", WebAuthnRegisterOptionsView.as_view(), name="webauthn-register-options"),
    path("webauthn/register/complete/", WebAuthnRegisterCompleteView.as_view(), name="webauthn-register-complete"),
    path("webauthn/auth/options/", WebAuthnAuthOptionsView.as_view(), name="webauthn-auth-options"),
    path("webauthn/auth/complete/", WebAuthnAuthCompleteView.as_view(), name="webauthn-auth-complete"),
]
