# University E-Voting (Dev)

Quick start (development):

1. Create virtualenv and install dependencies

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -U pip setuptools wheel
pip install -r requirements.txt
```

2. Run migrations and create superuser

```bash
python manage.py migrate
python manage.py createsuperuser
```

3. Run dev server

```bash
python manage.py runserver
```

4. Running tests

```bash
python manage.py test
```

Notes
- This repo contains scaffolding for a production-grade university e-voting system. The `voting.crypto` module provides RSA keypair generation and encryption helpers.

Key generation

Create keys (saved to `VOTE_KEYS_DIR` defined in `evoting_system/settings.py`). You can generate vote encryption keys and tally signing keys. Example:

```bash
. .venv/bin/activate
# generate vote encryption keys (defaults to names in settings)
python manage.py generate_keys --bits 2048 --private-file private_key.pem --public-file public_key.pem
# generate tally signing keypair
python manage.py generate_keys --bits 2048 --private-file tally_sign_private.pem --public-file tally_sign_public.pem
```

Notes on signing & tallying

- Encrypted payloads are signed by the tally signing key (`tally_sign_private.pem`) at cast time (if the signing key exists). Signatures are verified during tally; votes with invalid/missing signatures are treated as invalid and not counted. This makes tampering with stored encrypted payloads detectable.
- The `tally_votes` management command verifies signatures before decrypting votes.
- The private key must be kept secret (do not commit `keys/`), protect it with proper ACLs or secrets manager in production.

Security
- Never commit `keys/` directory to source control. Keep private key protected and access-limited.
