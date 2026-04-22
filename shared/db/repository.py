"""
Typed CRUD for all Supabase tables.

All methods are static/class methods so they can be called without
instantiating — keeps the handler code clean.

Step 3 of build order: implement after running migrations.
"""
from __future__ import annotations

from shared.db.client import get_supabase
from shared.models import Profile, WatchlistEntry, SeenEvent


class ProfileRepo:
    TABLE = "profiles"

    @classmethod
    async def get_or_create(cls, agent_address: str) -> Profile:
        """Return the profile for this agent address, creating one if absent."""
        raise NotImplementedError("ProfileRepo.get_or_create — implement in step 3")

    @classmethod
    async def update(cls, user_id: str, updates: dict) -> Profile:
        raise NotImplementedError("ProfileRepo.update — implement in step 3")

    @classmethod
    async def get_digest_subscribers(cls) -> list[Profile]:
        """Return all profiles with digest_opt_in=true and a valid email."""
        raise NotImplementedError("ProfileRepo.get_digest_subscribers — implement in step 12")


class WatchlistRepo:
    TABLE = "watchlist"

    @classmethod
    async def add(cls, user_id: str, event_id: str) -> WatchlistEntry:
        """Idempotent — upsert on (user_id, event_id)."""
        raise NotImplementedError("WatchlistRepo.add — implement in step 9")

    @classmethod
    async def remove(cls, user_id: str, event_id: str) -> None:
        raise NotImplementedError("WatchlistRepo.remove — implement in step 9")

    @classmethod
    async def list_for_user(cls, user_id: str) -> list[WatchlistEntry]:
        raise NotImplementedError("WatchlistRepo.list_for_user — implement in step 9")


class SeenRepo:
    TABLE = "seen_events"

    @classmethod
    async def log(
        cls,
        user_id: str,
        event_id: str,
        rating: int | None,
        notes: str | None,
    ) -> SeenEvent:
        """Upsert on (user_id, event_id) — repeated calls update, never duplicate."""
        raise NotImplementedError("SeenRepo.log — implement in step 9")


class DigestLogRepo:
    TABLE = "digest_log"

    @classmethod
    async def record(cls, user_id: str, event_count: int, status: str) -> None:
        raise NotImplementedError("DigestLogRepo.record — implement in step 12")
