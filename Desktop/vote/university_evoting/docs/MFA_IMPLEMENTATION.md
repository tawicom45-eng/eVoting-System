MFA (TOTP + WebAuthn) Implementation (POC)

- Models:
  - `MFATOTPDevice` stores TOTP secret, label, confirmation state
  - `WebAuthnCredential` stores public key and sign count for WebAuthn

- Endpoints:
  - `POST /api/auth/mfa/totp/register/` -> generate a TOTP secret and return provisioning URI
  - `POST /api/auth/mfa/totp/verify/` -> verify a TOTP code and confirm the device
  - `GET /api/auth/mfa/totp/` -> list registered TOTP devices
  - `DELETE /api/auth/mfa/totp/{id}/` -> revoke a TOTP device

- Notes:
  - TOTP uses `pyotp` and stores the base32 secret in the DB for the POC. In production this should be stored encrypted and protected.
  - WebAuthn endpoints are scaffolded via `WebAuthnCredential` model; full registration/attestation flows will follow using `fido2`.
