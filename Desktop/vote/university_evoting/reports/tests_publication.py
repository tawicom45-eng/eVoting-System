from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.management import call_command
from elections.models import Election
from reports.models import Report, ResultPublication
from audit.models import AuditLog
from django.contrib.auth.models import Permission


class PublicationWorkflowTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.reviewer = User.objects.create_user(username="rev", password="pass")
        self.publisher = User.objects.create_user(username="pub", password="pass")

        # assign permissions
        review_perm = Permission.objects.get(codename="can_review_publication")
        publish_perm = Permission.objects.get(codename="can_publish_publication")
        self.reviewer.user_permissions.add(review_perm)
        self.publisher.user_permissions.add(publish_perm)

        from django.utils import timezone
        now = timezone.now()
        self.election = Election.objects.create(name="Test Election", start_time=now, end_time=now)
        self.report = Report.objects.create(name="Tally Report")
        self.pub = ResultPublication.objects.create(election=self.election, report=self.report)

    def test_review_and_publish_flow(self):
        # reviewer marks reviewed
        self.pub.mark_reviewed(self.reviewer)
        self.pub.refresh_from_db()
        self.assertEqual(self.pub.status, ResultPublication.STATUS_REVIEWED)
        self.assertIsNotNone(self.pub.reviewed_at)

        # publisher publishes via command
        call_command("publish_results", "--publication-id", str(self.pub.pk), "--publisher-id", str(self.publisher.pk))
        self.pub.refresh_from_db()
        self.assertEqual(self.pub.status, ResultPublication.STATUS_PUBLISHED)
        self.assertIsNotNone(self.pub.published_at)

        # check audit logs
        logs = AuditLog.objects.filter(action__contains=f"Published results for publication {self.pub.pk}")
        self.assertTrue(logs.exists())

    def test_publisher_cannot_be_reviewer(self):
        self.pub.mark_reviewed(self.reviewer)
        with self.assertRaises(PermissionError):
            self.pub.publish(self.reviewer)

    def test_publish_requires_review(self):
        with self.assertRaises(ValueError):
            self.pub.publish(self.publisher)
