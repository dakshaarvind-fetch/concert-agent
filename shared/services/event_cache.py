"""24-hour event cache layer on top of Supabase events_cache — step 4."""


async def get_cached_events(query_key: str) -> list[dict] | None:
    """Return cached events for this query key if not expired, else None."""
    raise NotImplementedError("event_cache.get_cached_events — implement in step 4")


async def cache_events(query_key: str, events: list[dict]) -> None:
    """Write events to events_cache with expires_at = now() + 24h."""
    raise NotImplementedError("event_cache.cache_events — implement in step 4")
