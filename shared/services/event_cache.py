"""24-hour event cache layer on top of Supabase events_cache — step 4."""
from __future__ import annotations

from datetime import datetime, timezone


async def get_cached_events(city: str, start_date: str, end_date: str) -> list[dict] | None:
    """Return non-expired cached events for city+date range, or None on cache miss."""
    from shared.db.client import get_supabase

    db = get_supabase()
    now = datetime.now(timezone.utc).isoformat()

    result = (
        db.table("events_cache")
        .select("*")
        .eq("city", city.lower())
        .gte("starts_at", start_date)
        .lte("starts_at", end_date)
        .gt("expires_at", now)
        .execute()
    )
    return result.data if result.data else None


async def cache_events(events: list[dict]) -> None:
    """Upsert events into events_cache. expires_at defaults to now()+24h in the DB."""
    if not events:
        return
    from shared.db.client import get_supabase

    db = get_supabase()
    # Strip the raw field for the upsert rows to keep payload size manageable;
    # raw is useful for debugging but not needed for the pipeline.
    rows = [{k: v for k, v in e.items() if k != "raw"} for e in events]
    db.table("events_cache").upsert(rows, on_conflict="id").execute()
