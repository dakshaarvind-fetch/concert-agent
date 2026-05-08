"""
Intent parser tests — step 6.

Run with: pytest tests/test_intent_parser.py
"""
from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock, patch

import pytest

from shared.models import DateRange, Intent, SearchFilters

SENDER = "agent1qtestconcierge000000000000000000"


def _intent(**kwargs) -> Intent:
    defaults = dict(type="help", user_id="", agent_address=SENDER)
    return Intent(**{**defaults, **kwargs})


# ── Unit tests (LLM mocked) ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_parse_search_intent():
    """Search message → type=search with city and genres extracted."""
    mock_result = _intent(
        type="search",
        filters=SearchFilters(
            city="London",
            genres=["indie", "rock"],
            date_range=DateRange(start=date(2026, 5, 1), end=date(2026, 5, 31)),
        ),
        raw_query="Find indie rock shows in London next month",
    )

    with patch("shared.services.intent_parser._llm") as mock_llm_fn:
        mock_llm_fn.return_value = AsyncMock(ainvoke=AsyncMock(return_value=mock_result))
        from shared.services.intent_parser import parse_intent
        result = await parse_intent("Find indie rock shows in London next month", SENDER)

    assert result.type == "search"
    assert result.agent_address == SENDER
    assert result.filters.city == "London"
    assert "indie" in result.filters.genres


@pytest.mark.asyncio
async def test_parse_watchlist_intent():
    """Watchlist message → type=add_watchlist with event_name."""
    mock_result = _intent(
        type="add_watchlist",
        event_name="LCD Soundsystem",
    )

    with patch("shared.services.intent_parser._llm") as mock_llm_fn:
        mock_llm_fn.return_value = AsyncMock(ainvoke=AsyncMock(return_value=mock_result))
        from shared.services.intent_parser import parse_intent
        result = await parse_intent("Save the LCD Soundsystem show to my watchlist", SENDER)

    assert result.type == "add_watchlist"
    assert result.event_name == "LCD Soundsystem"
    assert result.agent_address == SENDER


@pytest.mark.asyncio
async def test_parse_seen_intent():
    """Log-seen message → type=log_seen with rating."""
    mock_result = _intent(
        type="log_seen",
        event_name="Fred Again",
        rating=5,
        notes="energy was insane",
    )

    with patch("shared.services.intent_parser._llm") as mock_llm_fn:
        mock_llm_fn.return_value = AsyncMock(ainvoke=AsyncMock(return_value=mock_result))
        from shared.services.intent_parser import parse_intent
        result = await parse_intent("I went to Fred Again last night, 5 stars", SENDER)

    assert result.type == "log_seen"
    assert result.rating == 5
    assert result.agent_address == SENDER


@pytest.mark.asyncio
async def test_parse_help_intent():
    """Unclear message → type=help."""
    mock_result = _intent(type="help")

    with patch("shared.services.intent_parser._llm") as mock_llm_fn:
        mock_llm_fn.return_value = AsyncMock(ainvoke=AsyncMock(return_value=mock_result))
        from shared.services.intent_parser import parse_intent
        result = await parse_intent("what can you do?", SENDER)

    assert result.type == "help"
    assert result.agent_address == SENDER


@pytest.mark.asyncio
async def test_agent_address_always_overridden():
    """agent_address must come from sender, never from LLM output."""
    mock_result = _intent(type="help", agent_address="agent1qwrong000")

    with patch("shared.services.intent_parser._llm") as mock_llm_fn:
        mock_llm_fn.return_value = AsyncMock(ainvoke=AsyncMock(return_value=mock_result))
        from shared.services.intent_parser import parse_intent
        result = await parse_intent("hello", SENDER)

    assert result.agent_address == SENDER


# ── Integration test ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
@pytest.mark.integration
async def test_parse_intent_real_llm():
    """Hits real ASI:One API. Requires ASI_API_KEY in .env"""
    import os
    from dotenv import load_dotenv
    load_dotenv(override=True)

    if not os.getenv("ASI_API_KEY") or os.getenv("ASI_API_KEY") == "test-asi-key":
        pytest.skip("ASI_API_KEY not set")

    # Clear LRU cache so a fresh client is built with real settings
    from shared.services.intent_parser import _llm, parse_intent
    _llm.cache_clear()

    result = await parse_intent(
        "Find indie shows in London next weekend under £60",
        SENDER,
    )

    assert result.type == "search"
    assert result.agent_address == SENDER
    assert result.filters is not None  # guaranteed by parse_intent fallback
    print(f"\nParsed intent: type={result.type}, city={result.filters.city}, genres={result.filters.genres}, max_price={result.filters.max_price}")
