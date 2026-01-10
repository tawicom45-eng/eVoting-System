# Module 4 — Campaign & Poster Generation (Comprehensive)

## Overview
Provides tools to create campaign materials (posters, PDFs) consistent with university branding, with optional AI-assisted layout and QR code generation linking to candidate profiles.

## 1. Purpose
- Provide templated, accessible, and brand-compliant campaign assets for candidates
- Prevent misuse and ensure parity of exposure where required

## 2. Core Capabilities
- Template library with brand constraints
- Image processing pipeline (resize, compress, accessibility checks)
- AI layout assistant (optional) to generate poster drafts
- Export to print-ready PDF and web-optimized images
- QR code generation linking to candidate profile or manifesto

## 3. Data Model
```python
class PosterTemplate(models.Model):
    name = models.CharField(max_length=200)
    layout = models.JSONField()  # regions, fonts, rules
    brand_allowed = models.BooleanField(default=True)

class PosterAsset(models.Model):
    candidate = models.ForeignKey('voting.Candidate')
    template = models.ForeignKey(PosterTemplate)
    image = models.FileField()
    generated_at = models.DateTimeField(auto_now_add=True)
```

## 4. API Surface
- POST /api/candidates/{id}/poster/generate/ — generate poster (preview)
- GET /api/candidates/{id}/poster/{asset}/download/ — download image/PDF

## 5. Security & Moderation
- Require admin approval for outputs
- Optional AI content moderation to detect inappropriate materials

## 6. NFRs
- Poster generation latency under 10s for simple templates
- Generated outputs meet accessibility contrast guidelines

## 7. Acceptance Criteria
- Candidate can generate a poster preview; admin can approve for publication
- Posters are branded correctly and exportable to PDF

---
*Next: Deep-draft Election Management (Module 5).*