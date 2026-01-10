# Module 5 — Election Management (Comprehensive)

## Overview
Controls the full election lifecycle: creation, scheduling, templates, parallel elections, emergency pause, auto-archiving, and versioning of configs.

## 1. Purpose
- Provide robust tooling for configuring elections and ensuring safe state transitions.
- Support dry-run/testing and versioned configs for reproducibility.

## 2. Core Capabilities
- Election creation with config templates
- Scheduling and automatic state transitions
- Election config versioning and dry-run simulation
- Emergency pause/resume and scheduled auto-archive

## 3. Data Model
```python
class Election(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    state = models.CharField(choices=[('draft','Draft'),('scheduled','Scheduled'),('active','Active'),('paused','Paused'),('closed','Closed'),('archived','Archived')])
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    config = models.JSONField()  # includes positions, eligibility policy refs
    version = models.IntegerField(default=1)
```

## 4. API Surface
- POST /api/elections/ — create (with optional template)
- POST /api/elections/{id}/simulate/ — dry-run simulation
- POST /api/elections/{id}/pause/ — emergency pause
- POST /api/elections/{id}/state/ — manual state transitions (admin only)

## 5. Workflows
- Create -> configure positions -> lock ballots -> publish (schedule)
- Dry-run: simulate eligibility and turnout to validate configurations
- Versioning: each config change creates a new version with audit metadata

## 6. NFRs
- State transition must have strict audit trail and atomicity
- Scheduling precision to seconds for synchronized start/stop

## 7. Acceptance Criteria
- Ability to create, simulate, schedule and pause elections with audit
- Configs are versioned and snapshot-able for replays and audits

---
*Next: Deep-draft Voting Engine (Module 6).*