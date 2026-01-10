from django.shortcuts import redirect
from django.views import View
from django.contrib.auth import login, logout, get_user_model
from rest_framework import generics, permissions
from django.urls import reverse

from .models import ExternalIntegration
from .serializers import ExternalIntegrationSerializer
from .sso import DummySSOAdapterClient
from accounts.models import Profile


class ExternalIntegrationListView(generics.ListAPIView):
    permission_classes = (permissions.IsAdminUser,)
    queryset = ExternalIntegration.objects.all()
    serializer_class = ExternalIntegrationSerializer


class SSOLoginView(View):
    """A lightweight SSO login stub for development.

    Uses the DummySSOAdapterClient to obtain a test user, creates/updates a local
    User and Profile if needed, and logs the user into the session. Supports a
    `next` query parameter to redirect back to the original destination.
    """

    def get(self, request):
        next_url = request.GET.get('next') or '/'
        client = DummySSOAdapterClient()
        info = client.get_first_user()
        if not info:
            return redirect(next_url)

        User = get_user_model()
        user = User.objects.filter(username=info['username']).first()
        if not user:
            user = User.objects.create_user(username=info['username'], email=info.get('email'))
            user.set_unusable_password()
            user.save()
            Profile.objects.create(
                user=user,
                student_id=info.get('student_id'),
                role=info.get('role', 'student'),
                campus=info.get('campus', ''),
                faculty=info.get('faculty', ''),
                attributes=info.get('attributes', {}) or {},
            )
        else:
            # update profile attributes
            p = getattr(user, 'profile', None)
            if not p:
                Profile.objects.create(
                    user=user,
                    student_id=info.get('student_id'),
                    role=info.get('role', 'student'),
                    campus=info.get('campus', ''),
                    faculty=info.get('faculty', ''),
                    attributes=info.get('attributes', {}) or {},
                )
            else:
                p.student_id = info.get('student_id') or p.student_id
                p.role = info.get('role') or p.role
                p.campus = info.get('campus') or p.campus
                p.faculty = info.get('faculty') or p.faculty
                p.attributes.update(info.get('attributes', {}) or {})
                p.save()

        login(request, user)
        return redirect(next_url)


class SSOLogoutView(View):
    """Simple logout helper that clears the session and redirects to `next` or '/'."""

    def get(self, request):
        next_url = request.GET.get('next') or '/'
        logout(request)
        return redirect(next_url)
