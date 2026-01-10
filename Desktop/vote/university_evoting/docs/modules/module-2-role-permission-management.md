# Module 2 — Role & Permission Management (Comprehensive)

## Overview
Manages RBAC and ABAC, temporary/conditional privileges, approval workflows, and permission auditing. Designed to enforce least privilege across the platform.

## 1. Purpose
- Provide centralised permission management and policy evaluation service for RBAC and ABAC.
- Expose policy evaluation API for other services (Eligibility, Voting Engine, Admin UI).

## 2. Core Concepts
- Roles: named sets of permissions (voter, election-admin, auditor, super-admin)
- Permissions: atomic actions (e.g., votes.submit, elections.create)
- Policies: ABAC rules expressed as JSON logic or a policy language (Rego or Open Policy Agent)
- Role assignments: time-bound, with approval metadata

## 3. Data Model
```python
class Role(models.Model):
    name = models.CharField(max_length=64, unique=True)
    permissions = models.JSONField()  # list of permission strings

class UserRole(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    role = models.ForeignKey(Role)
    scope = models.JSONField(null=True)  # e.g., election_id or campus
    start_at = models.DateTimeField(null=True)
    end_at = models.DateTimeField(null=True)
    approved = models.BooleanField(default=False)
```

## 4. API Surface
- POST /api/roles/ — create role (admin)
- POST /api/roles/{role}/assign/ — assign role to user (with optional scope and approval)
- POST /api/authorization/evaluate/ — returns allow/deny + metadata (used by microservices)
- GET /api/roles/{role}/permissions/ — view permissions

## 5. Policy Engine
- Support offloading policy evaluation to OPA or a lightweight local engine
- Provide decision caching with short TTLs and immediate invalidation on policy changes

## 6. Workflows
- Role request: user requests a role -> approver notified -> approve/reject -> audit log
- Temporary roles auto-expire and generate notifications

## 7. Security & Audit
- Audit all role changes and policy updates with before/after state
- Encryption of sensitive policy artifacts at rest

## 8. NFRs
- Policy evaluation latency < 50ms P95
- Support tens of thousands of policy checks per second under load

## 9. Acceptance Criteria
- Services can call evaluation API and get consistent allow/deny decisions
- Role approval workflows with audit trails exist and tested

---
*Next: Deep-draft Candidate Management (Module 3).*