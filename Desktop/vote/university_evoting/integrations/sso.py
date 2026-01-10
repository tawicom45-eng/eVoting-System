"""SSO adapter scaffolding.

Provide an adapter interface for integrating with University SSO (SAML/LDAP/OIDC).
This is a lightweight POC adapter that can be extended to call real SSO endpoints or
plug into cloud identity providers.
"""
from typing import Iterable, Dict


class BaseSSOAdapter:
    """Base class to implement for specific SSO providers."""

    def fetch_users(self) -> Iterable[Dict]:
        """Yield user dicts with fields: username, email, student_id, role, campus, faculty, attributes"""
        raise NotImplementedError


class DummySSOAdapter(BaseSSOAdapter):
    """A dummy adapter for testing/dev that yields sample users."""

    def fetch_users(self):
        yield {"username": "sso_alice", "email": "sso_alice@example.com", "student_id": "SSO01", "role": "student", "campus": "Main", "faculty": "Science", "attributes": {"allowed_to_vote": True}}
        yield {"username": "sso_bob", "email": "sso_bob@example.com", "student_id": "SSO02", "role": "student", "campus": "East", "faculty": "Arts"}


# small helper to support SSO login stub
class DummySSOAdapterClient:
    def __init__(self, adapter: BaseSSOAdapter | None = None):
        self.adapter = adapter or DummySSOAdapter()

    def fetch_users(self):
        return self.adapter.fetch_users()

    def get_first_user(self):
        it = self.fetch_users()
        try:
            return next(it)
        except StopIteration:
            return None
