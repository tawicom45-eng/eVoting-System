from django.core.management.base import BaseCommand
from accounts.models import MFATOTPDevice
from accounts import crypto
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Re-encrypt stored MFA (TOTP) secrets using the current MFA_SECRET_FERNET_KEY'

    def handle(self, *args, **options):
        devices = MFATOTPDevice.objects.all()
        total = devices.count()
        reencrypted = 0
        skipped = 0
        for d in devices:
            try:
                plaintext = None
                try:
                    plaintext = crypto.decrypt_secret(d.secret)
                except Exception:
                    # if we can't decrypt with existing keys, log and skip
                    logger.warning(f"Unable to decrypt secret for device {d.id}; skipping")
                    skipped += 1
                    continue
                new_token = crypto.encrypt_secret(plaintext)
                if new_token != d.secret:
                    d.secret = new_token
                    d.save()
                    reencrypted += 1
            except Exception:
                logger.exception(f"Error re-encrypting device {d.id}")
        self.stdout.write(self.style.SUCCESS(f"Processed {total} devices, re-encrypted {reencrypted}, skipped {skipped}"))
