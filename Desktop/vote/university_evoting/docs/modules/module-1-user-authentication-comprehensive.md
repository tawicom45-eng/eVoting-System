# Module 1 — User & Authentication (Comprehensive)

## Overview
Merged responsibility: canonical user management and authentication/identity verification. This combined doc details user data, account lifecycle, SSO and passwordless flows, MFA, token lifecycle, and integration points with SIS and ABAC.

## 1. Purpose
- Provide canonical user identities and attributes (managed in User Management) and secure authentication and session management (Auth).
- Separation of concerns: User Management owns attributes and roles; Auth owns tokens, sessions, MFA, SSO.

## 2. Actors
- End users (students, staff)
- Admins, election operators
- Identity Providers (OIDC/SAML/LDAP)
- Device and risk services

## 3. Core Capabilities
- Bulk import and periodic SIS sync with reconciliation
- Local password login, OTP, passwordless (magic links), and SSO (OIDC/SAML)
- MFA (WebAuthn/TOTP) support and enforcement by policy
- JWT access tokens and rotating refresh tokens with reuse detection
- Device/session management and impersonation auditing (admin only)

## 4. Data Models (Django-style)
```python
# accounts.models.Profile exists (basic fields)
class User(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    # minimal PII; additional attributes in Profile

class Profile(models.Model):
    user = models.OneToOneField(User)
    student_id = models.CharField(max_length=64, unique=True, null=True)
    role = models.CharField(max_length=32)
    status = models.CharField(choices=STATUS_CHOICES, default='active')
    attributes = models.JSONField(default=dict)

class AuthSession(models.Model):
    user = models.ForeignKey(User)
    session_id = models.UUIDField(default=uuid.uuid4)
    device = models.JSONField(null=True)
    refresh_token_hash = models.CharField(max_length=128)
    created = models.DateTimeField(auto_now_add=True)
    revoked = models.BooleanField(default=False)
```

## 5. API Surface (examples)
- POST /api/accounts/import/ — upload SIS CSV or connector config (admin)
- POST /api/auth/login/ — returns access token + refresh token
- POST /api/auth/refresh/ — rotates refresh token
- POST /api/auth/passwordless/ — send magic link/OTP
- POST /api/auth/mfa/register/ — register device
- GET /api/accounts/{id}/ — read-only profile for users (limited fields)
- POST /api/accounts/{id}/roles/ — assign role (admin/approval)

## 6. Workflows
- Bulk import: validate CSV -> dry-run -> import -> reconcile -> create audit log
- Login: credential/SSO verification -> check Profile.status -> create AuthSession -> issue tokens
- Token rotation: on refresh, verify and rotate token, detect reuse
- MFA enforcement: policy check during login / sensitive actions

## 7. Security
- Hash refresh tokens only; JWT short lifetime; JWK endpoint for signature verification
- Enforce device binding for high-risk sessions (optional)
- Do not store raw IPs unless required; store hashed IPs for anomaly detection
- GDPR-style data minimization & soft-deletes

## 8. NFRs
- Login latency P95 < 250ms
- Availability 99.95% during elections
- Support one-time import of 100k users per hour

## 9. Monitoring & Audit
- Login success/failure rates, MFA enrollments, refresh token reuse events, SIS import metrics
- Audit trails for role assignments and profile changes

## 10. Acceptance Criteria
- SIS import works and produces reconciliation reports
- Users can authenticate with password and SSO; refresh rotation works
- MFA can be required by policy and enforced

---
*Next: Deep-draft Role & Permission Management (Module 2).*