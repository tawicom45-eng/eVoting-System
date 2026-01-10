"""Simple ABAC policy evaluator with pluggable caching.

This POC implements a few straightforward policies:
- admins can do anything
- users with profile.status != 'active' are denied for voting actions
- a profile.attributes flag 'allowed_to_vote': False denies voting actions

The evaluator uses Django's cache framework (configure a cache named 'abac' to use Redis
or another shared backend). A profile version key is incremented on profile change to
allow efficient invalidation without key enumeration. If no cache is configured this
falls back to a local LRU cache for the POC.
"""
from functools import lru_cache
import time
import logging
import hashlib
import json
from django.conf import settings
from django.core.cache import caches

logger = logging.getLogger(__name__)

DEFAULT_TTL = getattr(settings, 'ABAC_CACHE_TTL', 5)


def _compute_decision(user_id, action, resource, context_tuple):
    # context_tuple is a tuple of (key, value) pairs
    ctx = dict(context_tuple)
    profile = ctx.get("profile")
    # Support cached profile_key form: ('profile_key', (role, status, attributes_tuple))
    if profile is None and 'profile_key' in ctx:
        pk = ctx.get('profile_key')
        if pk is None:
            return False
        role, status, attributes_tuple = pk
        # reconstruct a minimal profile-like object
        profile = type("P", (), {})()
        profile.role = role
        profile.status = status
        attrs = dict(attributes_tuple) if attributes_tuple is not None else {}
        profile.attributes = attrs
    if profile is None:
        return False
    # admin bypass
    if profile.role == "admin":
        logger.debug("ABAC allow: admin", extra={"user_id": user_id, "action": action})
        return True
    # status check
    if profile.status != "active":
        logger.debug("ABAC deny: status not active", extra={"user_id": user_id, "action": action, "status": profile.status})
        return False
    # explicit attribute checks
    allowed = profile.attributes.get("allowed_to_vote") if hasattr(profile, 'attributes') else None
    if allowed is False and action in ("issue_token", "cast_vote"):
        logger.debug("ABAC deny: attribute denies voting", extra={"user_id": user_id, "action": action, "attributes": profile.attributes})
        return False
    # default allow for now
    logger.debug("ABAC allow: default", extra={"user_id": user_id, "action": action})
    return True


# Fallback LRU cached path for local dev / tests
@lru_cache(maxsize=2048)
def _evaluate_lru_cached(user_id, action, resource, context_tuple):
    return _compute_decision(user_id, action, resource, context_tuple)


def _get_cache():
    try:
        return caches['abac']
    except Exception:
        try:
            return caches['default']
        except Exception:
            return None


def _context_hash(context_tuple):
    # stable deterministic string hash of context tuple
    try:
        s = json.dumps(context_tuple, sort_keys=True, default=str)
    except Exception:
        s = str(context_tuple)
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


def _cache_key(user_id, action, resource, context_tuple, profile_version=0):
    ctx_hash = _context_hash(context_tuple)
    res = str(resource) if resource is not None else ""
    return f"abac:decision:{user_id}:{action}:{res}:{profile_version}:{ctx_hash}"


def evaluate(user, action, resource=None, context=None):
    ctx = context or {}
    profile = getattr(user, 'profile', None)
    # build a stable, hashable profile key for caching (avoid mutable model instances)
    if profile is not None:
        profile_key = (getattr(profile, 'role', None), getattr(profile, 'status', None), tuple(sorted(getattr(profile, 'attributes', {}).items())))
    else:
        profile_key = None
    logger.debug("ABAC evaluate called", extra={"user_id": getattr(user, 'id', None), "action": action, "profile": {"role": getattr(profile, 'role', None), "status": getattr(profile, 'status', None), "attributes": getattr(profile, 'attributes', None)}})
    # include profile_key and any context items in a deterministic tuple for caching
    context_items = tuple(sorted((k, v) for k, v in ctx.items()))
    context_tuple = (('profile_key', profile_key),) + context_items

    cache = _get_cache()
    if cache is None:
        # fallback to in-process LRU cache
        return _evaluate_lru_cached(user.id, action, resource, context_tuple)

    # include per-profile version to avoid key enumeration during invalidation
    profile_version_key = f"abac:profile_version:{user.id}"
    profile_version = cache.get(profile_version_key, 0)
    key = _cache_key(user.id, action, resource, context_tuple, profile_version=profile_version)
    cached = cache.get(key)
    if cached is not None:
        return cached
    # compute and set
    decision = _compute_decision(user.id, action, resource, context_tuple)
    try:
        cache.set(key, decision, DEFAULT_TTL)
    except Exception:
        logger.debug("ABAC cache set failed", exc_info=True)
    return decision


def invalidate_profile_cache(user_id):
    """Bump profile version for user to invalidate related ABAC cache keys."""
    cache = _get_cache()
    if cache is None:
        return
    key = f"abac:profile_version:{user_id}"
    try:
        # If cache backend supports incr, use it for an atomic increment
        if hasattr(cache, 'incr'):
            cache.incr(key)
        else:
            # otherwise set a new incremented value
            v = cache.get(key, 0) or 0
            cache.set(key, v + 1)
    except Exception:
        # ignore caching errors for now
        logger.debug("Failed to invalidate profile cache", exc_info=True)

