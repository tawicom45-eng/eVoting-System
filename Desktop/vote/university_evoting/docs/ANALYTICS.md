# Analytics module

This module provides an internal metric store for audit and ad-hoc analysis. It is intentionally lightweight and integrates with the existing `monitoring` facade.

Key features
- Persistent metric samples in `analytics.Metric` (name, value, recorded_at)
- `analytics.utils.record_metric(name, value)` best-effort function for persisting a sample
- `analytics.utils.aggregate_average(name, window_seconds=None)` for quick averages
- HTTP API:
  - `GET /api/analytics/metrics/?name=<name>&since=<ISO>&until=<ISO>` returns samples
  - `GET /api/analytics/metrics/aggregate/?name=<name>&window=<seconds>` returns an average
- Integration: `monitoring.increment()` will also call `analytics.record_metric()` on each increment as a best-effort persistence layer.

Operational notes
- The persistence is best-effort and will not raise on DB errors; use `prune_metrics` management command to remove stale samples.
- For heavy-duty analytics, replace or extend with time-series DB (InfluxDB, TimescaleDB) or push metrics to Prometheus/Pushgateway and use remote storage.

Query parameter timestamp formats
- Prefer ISO 8601 timestamps for `since` and `until` (e.g., `2026-01-05T14:38:55Z`). For timezone offsets include the `+` (e.g., `2026-01-05T14:38:55+00:00`) and ensure it is URL-encoded when used in query strings.
- As a best-effort compatibility measure, the server will attempt to recover timestamps where a `+` in the offset has been decoded as a space by retrying parsing after replacing spaces with `+`.
- If you control the client, prefer using `Z` for UTC or percent-encode the `+` to avoid ambiguity (e.g., `%2B00:00`).
