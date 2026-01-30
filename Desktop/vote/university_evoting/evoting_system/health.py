from django.http import JsonResponse
from django.db import connections

def health(request):
    """Lightweight health endpoint for readiness checks."""
    # Basic DB connectivity check (non-blocking)
    try:
        conn = connections['default']
        conn.ensure_connection()
        db_ok = True
    except Exception:
        db_ok = False

    status = 'ok' if db_ok else 'partial'
    return JsonResponse({'status': status, 'db': db_ok})
