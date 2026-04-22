"""
Pydantic v2 models for every boundary: API payloads, DB rows, LLM outputs,
intents. Stubs raise NotImplementedError until each step is implemented.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


# ── Filters ──────────────────────────────────────────────────────────────────

class DateRange(BaseModel):
    start: date
    end: date


class SearchFilters(BaseModel):
    city: str | None = None
    date_range: DateRange | None = None
    max_price: float | None = None
    genres: list[str] = Field(default_factory=list)
    vibe: str | None = None
    radius_km: int = 50


# ── Taste profile ─────────────────────────────────────────────────────────────

class TasteProfile(BaseModel):
    user_id: str
    favourite_artists: list[str] = Field(default_factory=list)
    favourite_genres: list[str] = Field(default_factory=list)
    vibe_descriptors: list[str] = Field(default_factory=list)
    # artist_embedding stored in Supabase as vector(1536), not in this model


# ── Raw events from external APIs ─────────────────────────────────────────────

class Venue(BaseModel):
    name: str
    address: str | None = None
    city: str | None = None
    country: str | None = None
    lat: float | None = None
    lng: float | None = None


class EventRaw(BaseModel):
    id: str
    source: Literal["ticketmaster", "songkick"]
    name: str
    artists: list[str] = Field(default_factory=list)
    venue: Venue
    starts_at: datetime | None = None
    price_min: float | None = None
    price_max: float | None = None
    ticket_url: str | None = None
    image_url: str | None = None
    genres: list[str] = Field(default_factory=list)
    description: str | None = None


class EventEnriched(EventRaw):
    """EventRaw + Spotify enrichment (popularity, audio features, etc.)."""
    spotify_popularity: int | None = None
    spotify_preview_url: str | None = None


class EventScored(EventEnriched):
    taste_fit_score: int = Field(ge=0, le=100)
    reasoning: str  # one sentence, written by Claude


# ── LLM structured outputs ───────────────────────────────────────────────────

class PickReasoning(BaseModel):
    reasoning: str = Field(
        description="One sentence explaining why this event fits the user's taste."
    )


# ── Intent (from intent_parser) ───────────────────────────────────────────────

class Intent(BaseModel):
    type: Literal[
        "search",
        "add_watchlist",
        "remove_watchlist",
        "log_seen",
        "update_profile",
        "help",
    ]
    user_id: str
    agent_address: str
    filters: SearchFilters | None = None
    raw_query: str | None = None
    event_id: str | None = None
    event_name: str | None = None
    rating: int | None = Field(default=None, ge=1, le=5)
    notes: str | None = None
    updates: dict | None = None


# ── DB row models (mirrors Supabase schema) ───────────────────────────────────

class Profile(BaseModel):
    id: str
    agent_address: str
    email: str | None = None
    location_city: str | None = None
    location_lat: float | None = None
    location_lng: float | None = None
    search_radius_km: int = 50
    digest_opt_in: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None


class WatchlistEntry(BaseModel):
    id: str
    user_id: str
    event_id: str
    added_at: datetime | None = None
    target_price: float | None = None
    notify_on_price_drop: bool = True


class SeenEvent(BaseModel):
    id: str
    user_id: str
    event_id: str
    attended: bool = False
    rating: int | None = Field(default=None, ge=1, le=5)
    notes: str | None = None
    attended_at: date | None = None
    created_at: datetime | None = None
