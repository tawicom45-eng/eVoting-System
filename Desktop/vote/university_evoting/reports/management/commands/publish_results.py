from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from reports.models import ResultPublication


class Command(BaseCommand):
    help = "Publish reviewed results (enforces dual-approval: reviewer != publisher)"

    def add_arguments(self, parser):
        parser.add_argument("--publication-id", type=int, help="ID of the ResultPublication to publish")
        parser.add_argument("--election-id", type=int, help="Election ID to find the latest reviewed publication")
        parser.add_argument("--publisher-id", type=int, help="User ID of the publisher (must have permission)")

    def handle(self, *args, **options):
        pub_id = options.get("publication_id")
        election_id = options.get("election_id")
        publisher_id = options.get("publisher_id")

        if not publisher_id:
            raise CommandError("--publisher-id is required to identify the publisher user")

        User = get_user_model()
        try:
            publisher = User.objects.get(pk=publisher_id)
        except User.DoesNotExist:
            raise CommandError(f"Publisher user id {publisher_id} not found")

        if not publisher.has_perm("reports.can_publish_publication"):
            raise CommandError("Publisher does not have permission to publish publications")

        if pub_id:
            try:
                pub = ResultPublication.objects.get(pk=pub_id)
            except ResultPublication.DoesNotExist:
                raise CommandError(f"Publication id {pub_id} not found")
        elif election_id:
            pubs = ResultPublication.objects.filter(election_id=election_id, status=ResultPublication.STATUS_REVIEWED).order_by("-reviewed_at")
            if not pubs.exists():
                raise CommandError("No reviewed publications found for election")
            pub = pubs.first()
        else:
            raise CommandError("Either --publication-id or --election-id must be provided")

        try:
            pub.publish(publisher)
            self.stdout.write(self.style.SUCCESS(f"Published publication {pub.pk} by user {publisher.pk}"))
        except Exception as e:
            raise CommandError(str(e))
