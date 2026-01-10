# Module 6 — Voting Engine (Comprehensive)

## Overview
Core secure vote capture and validation engine: token issuance, vote submission, idempotency, eligibility enforcement, and offline support.

## 1. Purpose
- Provide robust, high-availability vote submission APIs that ensure one-person-one-vote, prevent replay, and integrate with encryption/storage services.

## 2. Core Capabilities
- Issue one-time voting tokens and enforce single-use
- Capture encrypted votes with idempotency & deduplication
- Validate eligibility via ABAC/Eligibility service before accepting votes
- Provide receipts (public verification hashes) and support offline queueing
- Expose health and monitoring endpoints and metrics for rate-limits

## 3. Data Model
```python
class VoteToken(models.Model):
    token = models.UUIDField(unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    election = models.ForeignKey(Election)
    issued_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

class VoteSubmission(models.Model):
    election = models.ForeignKey(Election)
    ballot_snapshot = models.JSONField()
    receipt_hash = models.CharField(max_length=128)
    status = models.CharField(choices=[('accepted','accepted'),('rejected','rejected')])
    created_at = models.DateTimeField(auto_now_add=True)
```

## 4. API Surface
- POST /api/elections/{id}/tokens/claim/ — issue/claim a one-time token
- POST /api/elections/{id}/vote/ — submit vote (requires token + encrypted payload)
- GET /api/elections/{id}/receipt/{receipt_hash}/ — verify receipt

## 5. Workflows
- Token claim: authenticate user -> eligibility check -> issue token -> audit
- Vote submit: validate token, eligibility, ballot snapshot -> encrypt & store -> mark token used -> return receipt
- Offline: allow authenticated client to queue encrypted payloads locally and submit when online; server validates idempotency and ordering

## 6. Security
- Enforce TLS, CSRF protection for web flows, rate-limit vote submission endpoints
- Use HSM or KMS to manage encryption keys for vote encryption where possible
- Audit token issuance and reuse attempts

## 7. NFRs
- Handle traffic spikes (burst capacity > 10k requests/second)
- Token issuance atomic & idempotent
- Vote submission P95 latency < 500ms under normal load

## 8. Acceptance Criteria
- Users can claim tokens only if eligible
- Token reuse and replay attacks are detected and blocked
- Receipts verifiable and reproducible via public hash

---
*Next: Deep-draft Results & Tallying (Module 7).*