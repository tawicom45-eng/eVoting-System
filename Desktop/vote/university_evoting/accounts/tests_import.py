import tempfile
import csv
import json
from pathlib import Path
from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth import get_user_model
from accounts.models import Profile


class ImportUsersTests(TestCase):
    def test_import_csv_creates_users_and_profiles(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "users.csv"
            with open(p, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=["username", "email", "student_id", "role", "campus", "faculty", "attributes"])
                writer.writeheader()
                writer.writerow({"username": "alice", "email": "alice@example.com", "student_id": "S001", "role": "student", "campus": "Main", "faculty": "Science", "attributes": json.dumps({"allowed_to_vote": True})})
                writer.writerow({"username": "bob", "email": "bob@example.com", "student_id": "S002", "role": "student", "campus": "East", "faculty": "Arts"})

            call_command("import_users", str(p))
            User = get_user_model()
            self.assertTrue(User.objects.filter(username="alice").exists())
            self.assertTrue(Profile.objects.filter(student_id="S001").exists())

            # ensure ABAC picks up allowed_to_vote attribute
            from abac.policy import evaluate
            u = User.objects.get(username="alice")
            self.assertTrue(evaluate(u, 'cast_vote'))

    def test_import_json_and_update_existing(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "users.json"
            data = [
                {"username": "carol", "email": "carol@example.com", "student_id": "S003", "role": "staff", "campus": "North", "faculty": "Engineering"}
            ]
            p.write_text(json.dumps(data), encoding='utf-8')
            call_command("import_users", str(p))
            User = get_user_model()
            u = User.objects.get(username="carol")
            # now update using --update-existing
            data2 = [{"username": "carol", "email": "carol2@example.com", "faculty": "Science"}]
            p.write_text(json.dumps(data2), encoding='utf-8')
            call_command("import_users", str(p), "--update-existing")
            u.refresh_from_db()
            self.assertEqual(u.email, "carol2@example.com")
            self.assertEqual(u.profile.faculty, "Science")
