"""Simple metrics facade for optional Prometheus/Sentry integration.

- If prometheus_client is available, expose a Counter for named metrics.
- If sentry_sdk is available, provide a capture function.
- Otherwise, functions are no-ops to keep POC simple.
"""

try:
    from prometheus_client import Counter
    _counters = {}
    def increment(name, amount=1):
        c = _counters.get(name)
        if c is None:
            c = Counter(f"university_evoting_{name}", f"Counter for {name}")
            _counters[name] = c
        c.inc(amount)
        # best-effort also persist a sample to analytics DB if available
        try:
            from analytics.utils import record_metric
            record_metric(name, amount)
        except Exception:
            pass
except Exception:
    def increment(name, amount=1):
        # no-op for prometheus, but still try to persist a sample in analytics DB
        try:
            from analytics.utils import record_metric
            record_metric(name, amount)
        except Exception:
            return

try:
    import sentry_sdk
    def capture_message(msg, **kwargs):
        sentry_sdk.capture_message(msg, **kwargs)
except Exception:
    def capture_message(msg, **kwargs):
        return
