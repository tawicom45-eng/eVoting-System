# Module 7 — Results & Tallying (Comprehensive)

## Overview
Responsible for secure, verifiable tallying and publication of results, with multi-stage approvals and signed artifacts.

## 1. Purpose
- Provide reproducible tallying pipelines with auditability and digital signatures for published results.

## 2. Core Capabilities
- Deterministic tally algorithms (supporting various voting systems)
- Recount & audit support
- Digitally sign published results (tally signing key, HSM/KMS integration)
- Result publication with access controls and delayed visibility options

## 3. Data Model
```python
class TallyRun(models.Model):
    election = models.ForeignKey(Election)
    run_at = models.DateTimeField(auto_now_add=True)
    results = models.JSONField()
    signed = models.BooleanField(default=False)
    signature = models.TextField(null=True)
```

## 4. APIs & CLI
- POST /api/tally/{election}/run/ — start a tally run (admin)
- GET /api/tally/{election}/results/ — retrieve signed results
- Management command: `manage.py run_tally <election_id>` for reproducible runs

## 5. Workflows
- Seal storage snapshot at close -> run tally on sealed snapshot -> validate inputs -> publish signed result
- Multi-stage approval to publish: run -> review -> sign & publish

## 6. Security & Reproducibility
- Provide full provenance (storage snapshot hashes, versioned configs) for each tally
- All published results must include signature verifiable by the public key

## 7. NFRs
- Tally process must be reproducible and have documented inputs/outputs
- Signing keys in HSM with auditable key usage logs

## 8. Acceptance Criteria
- Signed results reproducible by running tally against archived snapshot
- Multi-stage approval required for publication

---
*Next: Deep-draft Audit & Logging (Module 8).*