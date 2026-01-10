# QR Code Module

Purpose
- Secure voter verification
- Candidate authenticity validation
- One-person-one-vote enforcement
- Fast, contactless voting

Overview
- QR codes carry a cryptographically signed token (no PII inside). The token is time-limited and single-use.
- The backend verifies the token, ensures eligibility and that the token has not been used before, and then allows the voter to cast an encrypted vote.

Types of QR codes
1. Voter QR Code: per-voter, one-time use, short TTL.
2. Candidate QR Code: per-candidate, persistent for the election.
3. Election QR Code: identifies/validates an election (informational).

Key implementation points
- Tokens are produced by `voting.utils_qr.generate_signed_qr_token(user_id, candidate_id)`.
- Token verification done by `voting.utils_qr.verify_signed_qr_token(token)`.
- Replay prevention via `voting.models.QRTokenUsage` and `voting.models.QRLink`.
- Votes must be encrypted and stored separately from QR tokens; QR tokens are only used to authorize a vote.

Offline voting (notes)
- Tokens can be pre-generated and distributed to kiosks. Kiosks should store encrypted votes locally and sync when online, verifying tokens during sync and rejecting duplicates.

Audit & Logging
- All QR actions (issue, verify, use) should be logged to the audit module for traceability.

Where to find code
- Models: `voting/models.py`
- Utilities: `voting/utils_qr.py`
- Tests: `voting/tests/test_qr_module.py`

Next steps
- Add admin UI for issuing per-voter QR tokens.
- Add short-lived API endpoints for QR issuance and verification.
- Consider WebAuthn / MFA gating for high-value elections.
