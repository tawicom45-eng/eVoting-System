# Module 3 — Candidate Management (Comprehensive)

## Overview
Manages candidate applications, profiles, approvals, documents, campaigns compliance and candidate lifecycle.

## 1. Purpose
- Provide a secure, auditable pipeline for candidate registration and verification.
- Store candidate metadata and attachments, and enforce campaign compliance rules.

## 2. Core Capabilities
- Candidate application form and validation
- Upload and store manifestos and supporting docs (virus-scanned)
- Approval workflow with audit trail
- Candidate profile publishing and visibility controls
- Campaign violation tracking and sanctions

## 3. Data Model
```python
class CandidateApplication(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    position = models.ForeignKey('elections.Position')
    manifesto = models.FileField(null=True)
    status = models.CharField(choices=[('pending','pending'),('approved','approved'),('rejected','rejected')])
    notes = models.TextField(null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
```

## 4. API Surface
- POST /api/elections/{election}/positions/{position}/candidates/ — apply
- GET /api/candidates/ — list (filters: election, position, status)
- POST /api/candidates/{id}/status/ — approve/reject with reasons

## 5. Workflows
- Validation pipeline: form validation -> duplicate detection -> eligibility check -> submit
- Approval flow: reviewer queues, approval/rejection with reasons -> notifications
- Manifesto storage: store in protected storage with signed URLs for authorized access

## 6. Security & Compliance
- Virus-scan uploads (ClamAV or similar), content moderation (optional)
- Preserve audit trail for changes and approvals

## 7. NFRs
- Upload latency under 2s for small files (<5MB)
- Audit logs immutable for 7 years (configurable)

## 8. Acceptance Criteria
- Candidates can apply and are approved/rejected through workflow
- Manifestos are stored securely and retrievable by authorized viewers

---
*Next: Deep-draft Campaign & Poster Generation (Module 4).*