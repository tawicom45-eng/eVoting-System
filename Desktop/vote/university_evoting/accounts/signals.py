from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.contrib.sessions.models import Session
from django.dispatch import receiver
from django.utils import timezone


@receiver(user_logged_in)
def on_user_logged_in(sender, request, user, **kwargs):
    # Ensure session exists
    if not request.session.session_key:
        request.session.save()

    current_key = request.session.session_key
    # Remove other sessions for this user (enforce single active session)
    try:
        for s in Session.objects.exclude(session_key=current_key):
            try:
                data = s.get_decoded()
                if str(data.get('_auth_user_id')) == str(user.pk):
                    s.delete()
            except Exception:
                continue
    except Exception:
        pass

    # create an AuthSession record for auditing
    try:
        from .models import AuthSession
        device = {'ua': request.META.get('HTTP_USER_AGENT', '')}
        auth = AuthSession.objects.create(user=user, device=device)
        request.session['auth_session_id'] = str(auth.session_id)
        request.session['last_activity'] = int(timezone.now().timestamp())
    except Exception:
        pass


@receiver(user_logged_out)
def on_user_logged_out(sender, request, user, **kwargs):
    # Mark auth session revoked if present
    try:
        from .models import AuthSession
        sid = request.session.get('auth_session_id')
        if sid:
            AuthSession.objects.filter(session_id=sid).update(revoked=True)
    except Exception:
        pass
