"""
LangGraph pipeline — step 5 skeleton, steps 7-8 fill in scoring and reasoning.

Four nodes:
  load_profile → fetch_events → score → rank → END
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import TypedDict

from langgraph.graph import END, StateGraph

from shared.models import SearchFilters, TasteProfile


class ConciergeState(TypedDict):
    user_id: str
    agent_address: str
    query: str | None
    filters: SearchFilters
    taste_profile: TasteProfile
    raw_events: list[dict]
    scored_events: list[dict]
    final_picks: list[dict]
    errors: list[str]


# ── Node 1 ────────────────────────────────────────────────────────────────────

async def load_taste_profile(state: ConciergeState) -> dict:
    """Load (or create) profile + taste data from Supabase."""
    from shared.db.client import get_supabase

    db = get_supabase()

    # get_or_create profile
    res = (
        db.table("profiles")
        .select("*")
        .eq("agent_address", state["agent_address"])
        .maybe_single()
        .execute()
    )
    if res.data:
        profile = res.data
    else:
        profile = (
            db.table("profiles")
            .insert({"agent_address": state["agent_address"]})
            .execute()
        ).data[0]

    user_id: str = profile["id"]

    # load taste profile
    taste_res = (
        db.table("taste_profiles")
        .select("*")
        .eq("user_id", user_id)
        .maybe_single()
        .execute()
    )
    if taste_res.data:
        t = taste_res.data
        taste = TasteProfile(
            user_id=user_id,
            favourite_artists=t.get("favourite_artists") or [],
            favourite_genres=t.get("favourite_genres") or [],
            vibe_descriptors=t.get("vibe_descriptors") or [],
        )
    else:
        taste = TasteProfile(user_id=user_id)

    return {
        "user_id": user_id,
        "taste_profile": taste,
        # propagate profile city into filters if filter has no city set
        "filters": SearchFilters(
            **{
                **state["filters"].model_dump(),
                "city": state["filters"].city or profile.get("location_city"),
            }
        ),
    }


# ── Node 2 ────────────────────────────────────────────────────────────────────

async def fetch_events_parallel(state: ConciergeState) -> dict:
    """Fetch from Ticketmaster; fall back to Eventbrite if < 5 results."""
    from shared.tools.ticketmaster import search_ticketmaster_events

    filters = state["filters"]
    today = date.today()
    start = filters.date_range.start.isoformat() if filters.date_range else today.isoformat()
    end = filters.date_range.end.isoformat() if filters.date_range else (today + timedelta(days=30)).isoformat()
    city = filters.city or "London"

    events: list[dict] = await search_ticketmaster_events.ainvoke({
        "city": city,
        "start_date": start,
        "end_date": end,
        "genres": filters.genres or None,
        "radius_km": filters.radius_km,
        "max_price": filters.max_price,
    })

    # Eventbrite fallback when Ticketmaster returns fewer than 5 results
    if len(events) < 5:
        try:
            from shared.tools.eventbrite import search_eventbrite_events
            eb = await search_eventbrite_events.ainvoke({
                "city": city,
                "start_date": f"{start}T00:00:00",
                "end_date": f"{end}T23:59:59",
                "genres": filters.genres or None,
                "radius_km": filters.radius_km,
            })
            seen = {e["name"] for e in events}
            events += [e for e in eb if e["name"] not in seen]
        except NotImplementedError:
            pass  # Eventbrite not yet implemented — skipped silently

    return {"raw_events": events}


# ── Node 3 ────────────────────────────────────────────────────────────────────

async def score_by_taste_fit(state: ConciergeState) -> dict:
    """
    Keyword-overlap scoring until pgvector embeddings are wired in step 8.
    Step 8 replaces _simple_score with cosine similarity against artist_embedding.
    """
    taste = state["taste_profile"]
    scored = [
        {**e, "taste_fit_score": _simple_score(e, taste), "reasoning": ""}
        for e in state["raw_events"]
    ]
    return {"scored_events": scored}


def _simple_score(event: dict, taste: TasteProfile) -> int:
    score = 50
    event_genres = {g.lower() for g in event.get("genres", [])}
    taste_genres = {g.lower() for g in taste.favourite_genres}
    score += min(len(event_genres & taste_genres) * 15, 30)
    event_artists = {a.lower() for a in event.get("artists", [])}
    if event_artists & {a.lower() for a in taste.favourite_artists}:
        score += 20
    return min(score, 100)


# ── Node 4 ────────────────────────────────────────────────────────────────────

async def rank_and_reason(state: ConciergeState) -> dict:
    """
    Sort by score, keep top picks. Step 8 adds ASI:One reasoning per pick.
    Threshold is 50 for now (step 8 raises it to 75 with real embeddings).
    """
    ranked = sorted(state["scored_events"], key=lambda e: e["taste_fit_score"], reverse=True)
    picks = [e for e in ranked if e["taste_fit_score"] >= 50][:10]
    return {"final_picks": picks}


# ── Graph ─────────────────────────────────────────────────────────────────────

_graph = None


def build_graph():
    global _graph
    if _graph is not None:
        return _graph

    sg = StateGraph(ConciergeState)
    sg.add_node("load_profile", load_taste_profile)
    sg.add_node("fetch_events", fetch_events_parallel)
    sg.add_node("score", score_by_taste_fit)
    sg.add_node("rank", rank_and_reason)

    sg.set_entry_point("load_profile")
    sg.add_edge("load_profile", "fetch_events")
    sg.add_edge("fetch_events", "score")
    sg.add_edge("score", "rank")
    sg.add_edge("rank", END)

    _graph = sg.compile()
    return _graph


async def run_concierge_pipeline(
    agent_address: str,
    filters: SearchFilters,
    query: str | None = None,
    user_id: str = "",
) -> list[dict]:
    """Entry point called from the agent handler (step 7)."""
    result = await build_graph().ainvoke(
        ConciergeState(
            user_id=user_id,
            agent_address=agent_address,
            query=query,
            filters=filters,
            taste_profile=TasteProfile(user_id=user_id),
            raw_events=[],
            scored_events=[],
            final_picks=[],
            errors=[],
        )
    )
    return result["final_picks"]
