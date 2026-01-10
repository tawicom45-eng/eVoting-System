import csv
import json
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from accounts.models import Profile


class Command(BaseCommand):
    help = "Import users from CSV or JSON file into User and Profile models"

    def add_arguments(self, parser):
        parser.add_argument("file", help="Path to CSV or JSON file")
        parser.add_argument("--format", choices=["csv", "json"], help="File format (csv or json). If omitted infer from extension")
        parser.add_argument("--dry-run", action="store_true", help="Validate only; do not write to DB")
        parser.add_argument("--update-existing", action="store_true", help="Update existing users if present (match by username or student_id)")

    def handle(self, *args, **options):
        path = options["file"]
        fmt = options.get("format")
        dry_run = options.get("dry_run")
        update_existing = options.get("update_existing")

        if not fmt:
            if path.endswith(".csv"):
                fmt = "csv"
            elif path.endswith(".json"):
                fmt = "json"
            else:
                raise CommandError("Could not infer file format; provide --format")

        records = []
        if fmt == "csv":
            with open(path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    records.append(r)
        else:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    records = data
                else:
                    raise CommandError("JSON root must be an array of user objects")

        User = get_user_model()
        created = 0
        updated = 0
        skipped = 0
        for r in records:
            username = (r.get("username") or r.get("user") or r.get("email") or "").strip()
            email = (r.get("email") or "").strip()
            student_id = (r.get("student_id") or "").strip() or None
            role = (r.get("role") or "student").strip()
            campus = (r.get("campus") or "").strip()
            faculty = (r.get("faculty") or "").strip()
            attributes_raw = r.get("attributes")
            attributes = {}
            if attributes_raw:
                try:
                    if isinstance(attributes_raw, str):
                        attributes = json.loads(attributes_raw)
                    elif isinstance(attributes_raw, dict):
                        attributes = attributes_raw
                except Exception:
                    self.stderr.write(self.style.WARNING(f"Invalid attributes JSON for {username}; ignoring"))

            if not username:
                skipped += 1
                continue

            q = None
            if student_id:
                q = Profile.objects.filter(student_id=student_id).first()
            if not q:
                q = User.objects.filter(username=username).first()

            if q and isinstance(q, Profile):
                user = q.user
            elif q and isinstance(q, User):
                user = q
            else:
                user = None

            if user and not update_existing:
                skipped += 1
                continue

            if dry_run:
                # just validate
                created += 1 if not user else 0
                updated += 1 if user else 0
                continue

            if not user:
                # create user
                user = User.objects.create_user(username=username, email=email)
                user.set_unusable_password()
                user.save()
                p = Profile.objects.create(user=user, student_id=student_id, role=role, campus=campus, faculty=faculty, attributes=attributes)
                # invalidate ABAC cache for this profile
                try:
                    from abac.policy import invalidate_profile_cache
                    invalidate_profile_cache(user.id)
                except Exception:
                    pass
                created += 1
            else:
                # update
                p = getattr(user, 'profile', None)
                if not p:
                    p = Profile.objects.create(user=user, student_id=student_id, role=role, campus=campus, faculty=faculty, attributes=attributes)
                else:
                    p.student_id = student_id or p.student_id
                    p.role = role or p.role
                    p.campus = campus or p.campus
                    p.faculty = faculty or p.faculty
                    if attributes:
                        p.attributes.update(attributes)
                    p.save()
                # invalidate ABAC cache for this profile
                try:
                    from abac.policy import invalidate_profile_cache
                    invalidate_profile_cache(user.id)
                except Exception:
                    pass
                if email and user.email != email:
                    user.email = email
                    user.save()
                updated += 1

        self.stdout.write(self.style.SUCCESS(f"Import complete: created={created} updated={updated} skipped={skipped}"))
