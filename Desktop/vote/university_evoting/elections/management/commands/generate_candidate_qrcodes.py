import csv
import io
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from elections.models import Candidate

try:
    import qrcode
except Exception:
    qrcode = None


class Command(BaseCommand):
    help = "Generate QR codes for candidates. If 'qrcode' package is not installed, write a CSV of URLs instead."

    def add_arguments(self, parser):
        parser.add_argument("--output-dir", help="Directory to write QR PNGs or the CSV", default=None)
        parser.add_argument("--site-root", help="Site root to embed in QR URL, e.g. https://vote.university.edu", default="http://localhost:8000")

    def handle(self, *args, **options):
        outdir = options.get("output_dir")
        site_root = options.get("site_root")
        candidates = Candidate.objects.all()

        if qrcode is None:
            # write CSV with candidate id, name, url
            if not outdir:
                self.stdout.write(self.style.WARNING("qrcode package not installed and no output-dir specified; printing CSV to stdout"))
                f = io.StringIO()
                writer = csv.writer(f)
                writer.writerow(["candidate_id", "name", "qr_url"])
                for c in candidates:
                    writer.writerow([c.pk, c.name, c.get_absolute_qr_url(site_root)])
                self.stdout.write(f.getvalue())
                return
            os.makedirs(outdir, exist_ok=True)
            csv_path = os.path.join(outdir, "candidate_qr_urls.csv")
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["candidate_id", "name", "qr_url"])
                for c in candidates:
                    writer.writerow([c.pk, c.name, c.get_absolute_qr_url(site_root)])
            self.stdout.write(self.style.SUCCESS(f"Wrote CSV to {csv_path}"))
            return

        os.makedirs(outdir or settings.MEDIA_ROOT, exist_ok=True)
        outdir = outdir or settings.MEDIA_ROOT
        for c in candidates:
            url = c.get_absolute_qr_url(site_root)
            img = qrcode.make(url)
            fn = f"candidate_qr_{c.pk}.png"
            path = os.path.join(outdir, fn)
            img.save(path)
            self.stdout.write(self.style.SUCCESS(f"Wrote QR for candidate {c.pk} -> {path}"))
