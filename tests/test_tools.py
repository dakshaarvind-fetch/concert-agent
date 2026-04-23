"""
Tool-level tests — step 4.

Run unit tests:        pytest tests/test_tools.py
Run integration tests: pytest -m integration tests/test_tools.py
"""
from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ── Fixtures ──────────────────────────────────────────────────────────────────

TM_EVENT = {
    "id": "tm_abc123",
    "name": "Radiohead at O2",
    "url": "https://www.ticketmaster.com/event/tm_abc123",
    "images": [{"url": "https://img.tm.com/photo.jpg", "ratio": "16_9", "width": 1024}],
    "dates": {"start": {"dateTime": "2026-05-10T19:00:00Z"}},
    "classifications": [
        {"genre": {"name": "Rock"}, "subGenre": {"name": "Alternative Rock"}}
    ],
    "priceRanges": [{"min": 45.0, "max": 120.0}],
    "_embedded": {
        "venues": [{
            "name": "O2 Arena",
            "address": {"line1": "Peninsula Square"},
            "city": {"name": "London"},
            "country": {"name": "United Kingdom"},
            "location": {"latitude": "51.5032", "longitude": "-0.0033"},
        }],
        "attractions": [{"name": "Radiohead"}],
    },
}

TM_RESPONSE = {"_embedded": {"events": [TM_EVENT]}}


# ── Unit tests ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_ticketmaster_returns_events(mocker):
    """Mock HTTP — confirms tool parses response into normalised event dicts."""
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = TM_RESPONSE

    mock_get = AsyncMock(return_value=mock_resp)

    mocker.patch("shared.tools.ticketmaster.get_cached_events", return_value=None)
    mocker.patch("shared.tools.ticketmaster.cache_events", return_value=None)
    mocker.patch("shared.services.rate_limiter.ticketmaster_bucket.acquire", return_value=None)

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.get = mock_get
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        from shared.tools.ticketmaster import search_ticketmaster_events
        results = await search_ticketmaster_events.ainvoke({
            "city": "London",
            "start_date": "2026-05-01",
            "end_date": "2026-05-31",
        })

    assert len(results) == 1
    event = results[0]
    assert event["id"] == "tm_abc123"
    assert event["source"] == "ticketmaster"
    assert event["name"] == "Radiohead at O2"
    assert event["artists"] == ["Radiohead"]
    assert event["price_min"] == 45.0
    assert event["venue"]["city"] == "London"
    assert "Rock" in event["genres"]


@pytest.mark.asyncio
async def test_ticketmaster_uses_cache(mocker):
    """Cache hit should skip the HTTP call entirely."""
    cached = [{"id": "cached_1", "source": "ticketmaster", "name": "Cached Show"}]
    mocker.patch("shared.tools.ticketmaster.get_cached_events", return_value=cached)

    with patch("httpx.AsyncClient") as mock_client_cls:
        from shared.tools.ticketmaster import search_ticketmaster_events
        results = await search_ticketmaster_events.ainvoke({
            "city": "London",
            "start_date": "2026-05-01",
            "end_date": "2026-05-31",
        })
        mock_client_cls.assert_not_called()

    assert results == cached


@pytest.mark.asyncio
async def test_ticketmaster_max_price_filter(mocker):
    """max_price should filter out events with price_min above the limit."""
    events = [
        {"id": "1", "name": "Cheap Show", "price_min": 20.0},
        {"id": "2", "name": "Expensive Show", "price_min": 150.0},
    ]
    mocker.patch("shared.tools.ticketmaster.get_cached_events", return_value=events)

    from shared.tools.ticketmaster import search_ticketmaster_events
    results = await search_ticketmaster_events.ainvoke({
        "city": "London",
        "start_date": "2026-05-01",
        "end_date": "2026-05-31",
        "max_price": 50.0,
    })

    assert len(results) == 1
    assert results[0]["id"] == "1"


@pytest.mark.asyncio
async def test_rate_limiter_does_not_exceed_5rps():
    """Token bucket should not allow more than 5 requests per second."""
    import time
    from shared.services.rate_limiter import TokenBucket

    bucket = TokenBucket(rate=5.0, capacity=5.0)
    start = time.monotonic()
    for _ in range(6):
        await bucket.acquire()
    elapsed = time.monotonic() - start
    assert elapsed >= 0.19, f"Rate limiter too fast: {elapsed:.3f}s for 6 requests"


# ── Integration tests ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
@pytest.mark.integration
async def test_ticketmaster_real_api():
    """Hits real Ticketmaster API. Requires TICKETMASTER_API_KEY in .env"""
    import os
    from dotenv import load_dotenv
    load_dotenv()

    if not os.getenv("TICKETMASTER_API_KEY"):
        pytest.skip("TICKETMASTER_API_KEY not set")

    from shared.tools.ticketmaster import search_ticketmaster_events
    results = await search_ticketmaster_events.ainvoke({
        "city": "London",
        "start_date": "2026-05-01",
        "end_date": "2026-06-30",
        "size": 5,
    })

    assert isinstance(results, list)
    assert len(results) > 0
    first = results[0]
    assert first["source"] == "ticketmaster"
    assert first["id"]
    assert first["name"]
    print(f"\nGot {len(results)} events. First: {first['name']} @ {first['venue']['name']}")
