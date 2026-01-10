from django.urls import path
from .views import ExternalIntegrationListView, SSOLoginView, SSOLogoutView

urlpatterns = [
    path("", ExternalIntegrationListView.as_view(), name="api-integrations"),
    path("sso/login/", SSOLoginView.as_view(), name="integrations-sso-login"),
    path("sso/logout/", SSOLogoutView.as_view(), name="integrations-sso-logout"),
]
