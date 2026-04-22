"""
LangGraph pipeline — step 5 of build order (skeleton), steps 7-8 fill it in.

Five nodes:
  load_profile → fetch_events → enrich → score → rank_and_reason → END

All nodes raise NotImplementedError until implemented.
"""
from __future__ import annotations

from typing import TypedDict

from shared.models import (
    EventEnriched,
    EventRaw,
    EventScored,
    SearchFilters,
    TasteProfile,
)


class ConciergeState(TypedDict):
    user_id: str
    agent_address: str
    query: str | None
    filters: SearchFilters
    taste_profile: TasteProfile
    raw_events: list[EventRaw]
    enriched_events: list[EventEnriched]
    scored_events: list[EventScored]
    final_picks: list[EventScored]
    errors: list[str]


async def load_taste_profile(state: ConciergeState) -> dict:
    """Node 1: load taste profile from Supabase."""
    raise NotImplementedError("load_taste_profile — implement in step 5")


async def fetch_events_parallel(state: ConciergeState) -> dict:
    """Node 2: fetch from Ticketmaster + Songkick concurrently."""
    raise NotImplementedError("fetch_events_parallel — implement in step 5")


async def enrich_with_spotify(state: ConciergeState) -> dict:
    """Node 3: enrich events with Spotify popularity/preview data."""
    raise NotImplementedError("enrich_with_spotify — implement in step 8")


async def score_by_taste_fit(state: ConciergeState) -> dict:
    """Node 4: compute taste_fit_score for each event."""
    raise NotImplementedError("score_by_taste_fit — implement in step 8")


async def rank_and_reason(state: ConciergeState) -> dict:
    """Node 5: Claude writes one-sentence reasoning per pick."""
    raise NotImplementedError("rank_and_reason — implement in step 8")


def build_graph():
    """Construct and compile the LangGraph state machine."""
    raise NotImplementedError(
        "build_graph — implement in step 5. "
        "Wire the five nodes with StateGraph(ConciergeState)."
    )


async def run_concierge_pipeline(
    user_id: str,
    filters: SearchFilters,
    query: str | None = None,
    agent_address: str = "",
) -> list[EventScored]:
    """Entry point called from the agent handler."""
    raise NotImplementedError(
        "run_concierge_pipeline — implement in step 7 after graph and tools are ready."
    )
