from django.conf import settings
from cryptography.fernet import Fernet
import logging

logger = logging.getLogger(__name__)


_EPHEMERAL_KEY = None

def _get_fernet_instances():
    """Return a list of Fernet instances, ordered with the current key first.

    Supports settings:
      - MFA_SECRET_FERNET_KEY: single current base64 urlsafe key (bytes or str)
      - MFA_SECRET_FERNET_KEYS: iterable of keys (current first, older after)

    Keys may be str or bytes. If no keys are configured, this function will
    generate a process-local ephemeral key and log a warning so tests and
    development environments work without explicit configuration.
    """
    global _EPHEMERAL_KEY

    keys = None
    if hasattr(settings, 'MFA_SECRET_FERNET_KEYS') and getattr(settings, 'MFA_SECRET_FERNET_KEYS'):
        keys = list(getattr(settings, 'MFA_SECRET_FERNET_KEYS'))
    elif hasattr(settings, 'MFA_SECRET_FERNET_KEY') and getattr(settings, 'MFA_SECRET_FERNET_KEY'):
        keys = [getattr(settings, 'MFA_SECRET_FERNET_KEY')]

    if not keys:
        # No configured keys: use an ephemeral key for this process
        if _EPHEMERAL_KEY is None:
            _EPHEMERAL_KEY = Fernet.generate_key()
            logger.warning('No MFA Fernet keys configured; using an ephemeral key for this process. Set MFA_SECRET_FERNET_KEY(S) for persistent encryption.')
        keys = [_EPHEMERAL_KEY]

    instances = []
    for k in keys:
        if isinstance(k, str):
            k = k.encode('utf-8')
        instances.append(Fernet(k))
    return instances


def encrypt_secret(plaintext: str) -> str:
    """Encrypt plaintext using the current key (first key). Returns token str."""
    f = _get_fernet_instances()[0]
    token = f.encrypt(plaintext.encode('utf-8'))
    return token.decode('utf-8')


def decrypt_secret(token: str) -> str:
    """Attempt to decrypt token using available keys; return plaintext or raise."""
    instances = _get_fernet_instances()
    for f in instances:
        try:
            b = f.decrypt(token.encode('utf-8'))
            return b.decode('utf-8')
        except Exception:
            continue
    raise ValueError('Unable to decrypt MFA secret with configured keys')
