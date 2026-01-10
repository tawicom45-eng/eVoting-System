from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),  # include login/logout names
    path("api/accounts/", include("accounts.urls")),
    path("api/posters/", include("posters.urls")),
    path("api/auth/", include("accounts.auth_urls")),
    path("api/elections/", include("elections.urls")),
    path("api/voting/", include("voting.urls")),
    path("api/audit/", include("audit.urls")),
    path("api/reports/", include("reports.urls")),
    path("api/disputes/", include("disputes.urls")),
    path("api/integrations/", include("integrations.urls")),
    path("api/analytics/", include("analytics.urls")),
    path("metrics/", include("monitoring.urls")),
]
