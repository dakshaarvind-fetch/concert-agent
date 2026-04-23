"""
LangGraph pipeline tests — step 5.

Run with: pytest tests/test_graph.py
"""
from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from shared.models import DateRange, SearchFilters, TasteProfile

# ── Shared fixtures ───────────────────────────────────────────────────────────

FILTERS = SearchFilters(
    city="London",
    date_range=DateRange(start=date(2026, 5, 1), end=date(2026, 5, 31)),
)

TASTE = TasteProfile(
    user_id="test-uuid",
    favourite_artists=["Radiohead"],
    favourite_genres=["rock", "alternative"],
    vibe_descriptors=["intimate"],
)

FAKE_EVENTS = [
    {
        "id": "tm_1", "source": "ticketmaster", "name": "Radiohead Live",
        "artists": ["Radiohead"], "genres": ["Rock", "Alternative Rock"],
        "venue": {"name": "O2 Arena", "city": "London", "country": "UK",
                  "address": None, "lat": 51.5, "lng": -0.003},
        "city": "london", "starts_at": "2026-05-10T19:00:00Z",
        "price_min": 45.0, "price_max": 120.0,
        "ticket_url": "https://tm.com/1", "image_url": None,
        "description": None, "country": "UK", "lat": 51.5, "lng": -0.003,
    },
    {
        "id": "tm_2", "source": "ticketmaster", "name": "Some Jazz Band",
        "artists": ["Jazz Quartet"], "genres": ["Jazz"],
        "venue": {"name": "Ronnie Scott's", "city": "London", "country": "UK",
                  "address": None, "lat": 51.51, "lng": -0.13},
        "city": "london", "starts_at": "2026-05-15T20:00:00Z",
        "price_min": 25.0, "price_max": 40.0,
        "ticket_url": "https://tm.com/2", "image_url": None,
        "description": None, "country": "UK", "lat": 51.51, "lng": -0.13,
    },
]

FAKE_PROFILE_ROW = {
    "id": "test-uuid",
    "agent_address": "agent1qtest",
    "location_city": "London",
    "search_radius_km": 50,
    "digest_opt_in": True,
}

FAKE_TASTE_ROW = {
    "user_id": "test-uuid",
    "favourite_artists": ["Radiohead"],
    "favourite_genres": ["rock", "alternative"],
    "vibe_descriptors": ["intimate"],
}


def _mock_db(profile_row=FAKE_PROFILE_ROW, taste_row=FAKE_TASTE_ROW):
    """Build a minimal Supabase client mock that handles chained builder calls."""
    def make_chain(data):
        chain = MagicMock()
        chain.select.return_value = chain
        chain.eq.return_value = chain
        chain.insert.return_value = chain
        chain.maybe_single.return_value = chain
        chain.execute.return_value = MagicMock(data=data)
        return chain

    db = MagicMock()
    # First call → profiles table, second call → taste_profiles table
    db.table.side_effect = [
        make_chain(profile_row),
        make_chain(taste_row),
    ]
    return db


# ── Tests ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_pipeline_golden_path(mocker):
    """Full pipeline with mocked Supabase + Ticketmaster → returns ranked picks."""
    mocker.patch("shared.db.client.get_supabase", return_value=_mock_db())
    mocker.patch("shared.tools.ticketmaster.get_cached_events", return_value=None)
    mocker.patch("shared.tools.ticketmaster.cache_events", return_value=None)
    mocker.patch("shared.services.rate_limiter.ticketmaster_bucket.acquire", return_value=None)

    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {"_embedded": {"events": []}}

    with patch("httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_cls.return_value = mock_client

        # Bypass TM HTTP entirely — inject events directly via cache mock
        mocker.patch(
            "shared.tools.ticketmaster.get_cached_events",
            return_value=FAKE_EVENTS,
        )

        from shared.graph import build_graph, ConciergeState

        _graph = build_graph()
        result = await _graph.ainvoke(
            ConciergeState(
                user_id="",
                agent_address="agent1qtest",
                query=None,
                filters=FILTERS,
                taste_profile=TasteProfile(user_id=""),
                raw_events=[],
                scored_events=[],
                final_picks=[],
                errors=[],
            )
        )

    picks = result["final_picks"]
    assert len(picks) >= 1
    # Radiohead should score higher (artist + genre match)
    assert picks[0]["name"] == "Radiohead Live"
    assert picks[0]["taste_fit_score"] > picks[-1]["taste_fit_score"] or len(picks) == 1


@pytest.mark.asyncio
async def test_pipeline_empty_events(mocker):
    """Zero Ticketmaster results → Eventbrite attempted → empty picks returned gracefully."""
    mocker.patch("shared.db.client.get_supabase", return_value=_mock_db())
    mocker.patch("shared.tools.ticketmaster.get_cached_events", return_value=[])

    from shared.graph import build_graph, ConciergeState

    _graph = build_graph()
    result = await _graph.ainvoke(
        ConciergeState(
            user_id="",
            agent_address="agent1qtest",
            query=None,
            filters=FILTERS,
            taste_profile=TasteProfile(user_id=""),
            raw_events=[],
            scored_events=[],
            final_picks=[],
            errors=[],
        )
    )

    assert result["final_picks"] == []
    assert result["raw_events"] == []


@pytest.mark.asyncio
async def test_scoring_filters_low_scores():
    """Events scoring below 50 should not appear in final_picks."""
    from shared.graph import rank_and_reason

    scored = [
        {"id": "1", "name": "Great Match", "taste_fit_score": 80, "reasoning": ""},
        {"id": "2", "name": "Poor Match", "taste_fit_score": 30, "reasoning": ""},
        {"id": "3", "name": "Borderline", "taste_fit_score": 50, "reasoning": ""},
    ]
    result = await rank_and_reason(
        {"scored_events": scored, "raw_events": [], "final_picks": [], "errors": [],
         "user_id": "", "agent_address": "", "query": None,
         "filters": FILTERS, "taste_profile": TASTE}
    )

    ids = [e["id"] for e in result["final_picks"]]
    assert "1" in ids
    assert "3" in ids
    assert "2" not in ids
    # sorted highest first
    assert result["final_picks"][0]["id"] == "1"
