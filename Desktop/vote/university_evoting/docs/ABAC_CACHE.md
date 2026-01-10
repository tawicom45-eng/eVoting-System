ABAC Cache (Redis-backed) POC

- Behavior:
  - ABAC decisions are cached using Django cache framework. Configure a cache named `abac` for a Redis backend to enable shared caching across processes.
  - Cache keys include a per-profile version counter so invalidation is inexpensive: calling `invalidate_profile_cache(user_id)` bumps the version and automatically invalidates related keys.
  - Default TTL: `ABAC_CACHE_TTL` (default 5s). Fine-tune for your environment.

- Notes:
  - If no cache is configured, ABAC falls back to a local LRU cache for convenience in dev and tests.
