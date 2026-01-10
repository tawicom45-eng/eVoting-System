from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from integrations.sso import DummySSOAdapter
from accounts.models import Profile
import json


class Command(BaseCommand):
    help = "Sync users from the configured SSO adapter into local User/Profile models"

    def add_arguments(self, parser):
        parser.add_argument("--adapter", default="dummy", help="Adapter name to use (dummy)")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        adapter_name = options.get("adapter")
        dry = options.get("dry_run")
        if adapter_name == "dummy":
            adapter = DummySSOAdapter()
        else:
            raise ValueError("Unknown adapter")

        User = get_user_model()
        created = 0
        updated = 0
        for u in adapter.fetch_users():
            username = u.get("username")
            email = u.get("email")
            student_id = u.get("student_id")
            role = u.get("role", "student")
            campus = u.get("campus", "")
            faculty = u.get("faculty", "")
            attributes = u.get("attributes", {}) or {}

            existing = User.objects.filter(username=username).first()
            if existing and not dry:
                p = getattr(existing, 'profile', None)
                if not p:
                    p = Profile.objects.create(user=existing, student_id=student_id, role=role, campus=campus, faculty=faculty, attributes=attributes)
                else:
                    p.student_id = student_id or p.student_id
                    p.role = role or p.role
                    p.campus = campus or p.campus
                    p.faculty = faculty or p.faculty
                    p.attributes.update(attributes)
                    p.save()
                # invalidate ABAC cache for this profile
                try:
                    from abac.policy import invalidate_profile_cache
                    invalidate_profile_cache(existing.id)
                except Exception:
                    pass
                updated += 1
            elif not existing and not dry:
                user = User.objects.create_user(username=username, email=email)
                user.set_unusable_password()
                user.save()
                Profile.objects.create(user=user, student_id=student_id, role=role, campus=campus, faculty=faculty, attributes=attributes)
                # invalidate ABAC cache for this profile
                try:
                    from abac.policy import invalidate_profile_cache
                    invalidate_profile_cache(user.id)
                except Exception:
                    pass
