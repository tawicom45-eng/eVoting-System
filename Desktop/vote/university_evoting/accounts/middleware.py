import uuid
from django.http import JsonResponse
from .models import RevokedAccessToken
import logging

logger = logging.getLogger(__name__)

class RevokedAccessTokenMiddleware:
    """Middleware to reject requests with revoked JTI access tokens.

    Expects Authorization header in form: "Bearer <jti>.<random>" where <jti> is the UUID JTI.
    If the JTI exists in RevokedAccessToken and is revoked, respond with 401.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth = request.META.get("HTTP_AUTHORIZATION", "")
        if auth.startswith("Bearer "):
            token = auth.split(" ", 1)[1]
            parts = token.split(".")
            if parts:
                jti_str = parts[0]
                try:
                    jti = uuid.UUID(jti_str)
                    revoked = RevokedAccessToken.objects.filter(jti=jti, revoked=True).exists()
                    if revoked:
                        logger.warning("Request with revoked access token", extra={"jti": str(jti)})
                        return JsonResponse({"detail": "token revoked"}, status=401)
                except Exception:
                    # malformed JTI - ignore here and let auth fail downstream
                    pass
        return self.get_response(request)


class SessionIdleTimeoutMiddleware:
    """Middleware to enforce server-side session idle timeout.

    Stores last activity timestamp in the session under `last_activity`.
    If idle time exceeds `SESSION_IDLE_TIMEOUT` (seconds) the user is logged out.
    For AJAX/JSON requests returns 401 JSON; for regular requests redirects to `LOGIN_URL`.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            from django.conf import settings
            from django.utils import timezone
            now_ts = int(timezone.now().timestamp())
            timeout = getattr(settings, 'SESSION_IDLE_TIMEOUT', None)
            if timeout and getattr(request, 'user', None) and request.user.is_authenticated:
                last = request.session.get('last_activity')
                if last is not None:
                    try:
                        last = int(last)
                    except Exception:
                        last = None
                if last and (now_ts - last) > int(timeout):
                    # timeout expired: log out user
                    try:
                        from django.contrib.auth import logout
                        logout(request)
                        request.session.flush()
                    except Exception:
                        pass

                    # return JSON for AJAX/expecting JSON
                    accept = request.META.get('HTTP_ACCEPT', '')
                    is_ajax = request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' or 'application/json' in accept
                    from django.http import JsonResponse
                    if is_ajax:
                        return JsonResponse({'detail': 'session_expired'}, status=401)
                    else:
                        from django.shortcuts import redirect
                        login_url = getattr(settings, 'LOGIN_URL', '/accounts/login/')
                        return redirect(login_url)

                # update last activity
                request.session['last_activity'] = now_ts
        except Exception:
            # don't break requests on middleware errors
            logger.exception('SessionIdleTimeoutMiddleware error')

        return self.get_response(request)
