from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.shortcuts import redirect
from . import pages


def admin_root_redirect(request):
    """If a staff (non-superuser) visits /admin/ redirect to the custom admin dashboard.

    Otherwise, send to the normal admin login flow.
    """
    try:
        user = getattr(request, 'user', None)
        if user and user.is_authenticated and user.is_staff and not user.is_superuser:
            return redirect('accounts:admin-dashboard')
    except Exception:
        pass
    return redirect('/admin/login/?next=/admin/')

urlpatterns = [
    # Legacy/v1 voting booth alias (no /accounts/ prefix)
    path("voting/booth/<int:election_id>/", RedirectView.as_view(
        url="/accounts/voting/%(election_id)s/", permanent=False
    ), name="voting-booth-root-alias"),

    # Ensure /accounts/login/ uses our custom template before falling back to Django's auth views
    # Intercept exact /admin/ root to redirect staff users to the custom admin dashboard
    path('admin/', admin_root_redirect),
    path("admin/", admin.site.urls),
    # Custom account pages (login, register, etc.) should be matched first
    path("accounts/", include(("accounts.template_urls", "accounts"), namespace="accounts")),
    # Portal-specific auth endpoints (Option 4)
    path("accounts/", include("accounts.urls_portal")),
    # Django auth defaults (password reset, logout) remain available after our overrides
    path("accounts/", include("django.contrib.auth.urls")),

    # Public API endpoints used by templates
    path("api/login/", pages.login_api, name="api-login"),
    path("api/login/student/", pages.login_api_student, name="api-login-student"),
    path("api/login/staff/", pages.login_api_staff, name="api-login-staff"),
    path("api/login/admin/", pages.login_api_admin, name="api-login-admin"),
    path("api/register/", pages.register_api, name="api-register"),
    path("api/register/student/", pages.register_api_student, name="api-register-student"),
    path("api/register/staff/", pages.register_api_staff, name="api-register-staff"),
    path("api/register/admin/", pages.register_api_admin, name="api-register-admin"),
    path("api/password/send-code/", pages.send_password_code, name="send-password-code"),
    path("api/password/verify-code/", pages.verify_password_code, name="verify-password-code"),
    path("api/password/reset/", pages.reset_password, name="reset-password"),
    
    # API endpoints
    path("api/accounts/", include("accounts.urls")),
    path("api/posters/", include("posters.urls")),
    # Web-facing poster pages (forms, moderation UI, gallery)
    path("posters/", include("posters.urls")),
    # Dashboard pages (needed for template reverse lookups)
    path("dashboard/", include(("dashboard.urls", "dashboard"), namespace="dashboard")),
    path("api/auth/", include("accounts.auth_urls")),
    path("api/elections/", include("elections.urls")),
    path("api/voting/", include("voting.urls")),
    path("api/audit/", include("audit.urls")),
    path("api/reports/", include("reports.urls")),
    path("api/disputes/", include("disputes.urls")),
    path("api/integrations/", include("integrations.urls")),
    path("api/analytics/", include("analytics.urls")),
    path("api/ai/", include("ai_ops.urls")),
    # Portal-facing election pages (Option 4)
    path("elections/", include(("elections.portal_urls", "elections_portal"), namespace="elections_portal")),
    path("metrics/", include("monitoring.urls")),
]

# Error handlers
handler400 = 'accounts.template_views.bad_request'
handler403 = 'accounts.template_views.access_denied'
handler404 = 'accounts.template_views.page_not_found'
handler500 = 'accounts.template_views.server_error'

from django.views.generic import TemplateView, RedirectView
from . import health


class SafeTemplateView(TemplateView):
    """TemplateView that accepts POST by delegating to GET to avoid 500s

    Some pages are served as static templates and accidental POSTs (native
    form submits or misbehaving JS) can trigger method errors or server
    exceptions. This view simply treats POST the same as GET for safety.
    """
    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

# Global fallback for email verification URL name to prevent template reverse errors
urlpatterns.insert(0, path('verify-email/', TemplateView.as_view(template_name='accounts/email_verification.html'), name='verify-email'))

# Lightweight overrides for a few account pages to avoid deep template reverse errors
# Serve the full forget-password page provided in templates/accounts/forget-password.html
urlpatterns.insert(0, path('accounts/forget-password/', SafeTemplateView.as_view(template_name='accounts/forget-password.html'), name='forget-password'))
urlpatterns.insert(0, path('accounts/third-party-auth/', TemplateView.as_view(template_name='accounts/third_party_auth.html'), name='third-party-auth-mini'))

# Provide a top-level fallback for the frequently-referenced `election-list` name
urlpatterns.insert(0, path('elections/', TemplateView.as_view(template_name='accounts/election_list.html'), name='election-list'))
# Provide a top-level fallback for `election-watch` used in header templates
urlpatterns.insert(0, path('elections/watch/', TemplateView.as_view(template_name='accounts/election_watch.html'), name='election-watch'))

# Serve a modern landing page at root and add static text templates.
# Use SafeTemplateView so accidental POSTs don't cause server errors.
urlpatterns.insert(0, path('', SafeTemplateView.as_view(template_name='landing.html'), name='landing'))
urlpatterns += [
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('humans.txt', TemplateView.as_view(template_name='humans.txt', content_type='text/plain')),
    path('health/', health.health, name='health'),
]
