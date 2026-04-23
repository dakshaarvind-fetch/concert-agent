"""
Chat Protocol roundtrip tests — step 7.

Confirms: ChatMessage in → ChatAcknowledgement first → ChatMessage reply.
"""
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from shared.models import Intent, SearchFilters


def _make_intent(**kwargs) -> Intent:
    defaults = dict(type="help", user_id="", agent_address="agent1qtest123")
    return Intent(**{**defaults, **kwargs})


@pytest.mark.asyncio
async def test_handle_chat_sends_ack_before_reply(mocker):
    """First send must be ChatAcknowledgement, second must be ChatMessage reply."""
    mocker.patch(
        "shared.services.intent_parser.parse_intent",
        return_value=_make_intent(type="help"),
    )

    from uagents_core.contrib.protocols.chat import ChatAcknowledgement, ChatMessage, TextContent
    from agents.concierge.agent import handle_chat

    mock_ctx = MagicMock()
    mock_ctx.send = AsyncMock()
    mock_ctx.logger = MagicMock()

    msg = ChatMessage(
        timestamp=datetime.utcnow(),
        msg_id=uuid4(),
        content=[TextContent(type="text", text="hello")],
    )

    await handle_chat(mock_ctx, "agent1qtest123", msg)

    calls = mock_ctx.send.call_args_list
    assert len(calls) >= 2, "Expected at least 2 sends (ack + reply)"

    first_payload = calls[0].args[1]
    assert isinstance(first_payload, ChatAcknowledgement), (
        f"First send must be ChatAcknowledgement, got {type(first_payload)}"
    )

    second_payload = calls[1].args[1]
    assert isinstance(second_payload, ChatMessage), (
        f"Second send must be ChatMessage reply, got {type(second_payload)}"
    )


@pytest.mark.asyncio
async def test_handle_chat_ignores_empty_content(mocker):
    """Handler with no TextContent should only send ack, no reply."""
    mocker.patch("shared.services.intent_parser.parse_intent")

    from uagents_core.contrib.protocols.chat import ChatMessage
    from agents.concierge.agent import handle_chat

    mock_ctx = MagicMock()
    mock_ctx.send = AsyncMock()
    mock_ctx.logger = MagicMock()

    msg = ChatMessage(
        timestamp=datetime.utcnow(),
        msg_id=uuid4(),
        content=[],
    )

    await handle_chat(mock_ctx, "agent1qtest123", msg)

    calls = mock_ctx.send.call_args_list
    assert len(calls) == 1, "Should only send ack when there's no text content"


@pytest.mark.asyncio
async def test_handle_chat_search_returns_events(mocker):
    """Search intent triggers pipeline and returns formatted event list."""
    mocker.patch(
        "shared.services.intent_parser.parse_intent",
        return_value=_make_intent(
            type="search",
            filters=SearchFilters(city="London"),
            raw_query="shows in London",
        ),
    )
    mocker.patch(
        "shared.graph.run_concierge_pipeline",
        return_value=[{
            "id": "tm_1", "name": "Radiohead Live", "source": "ticketmaster",
            "venue": {"name": "O2 Arena", "city": "London"},
            "starts_at": "2026-05-10T19:00:00Z",
            "price_min": 45.0, "price_max": 120.0,
            "ticket_url": "https://tm.com/1",
            "taste_fit_score": 85, "reasoning": "",
        }],
    )

    from uagents_core.contrib.protocols.chat import ChatMessage, TextContent
    from agents.concierge.agent import handle_chat

    mock_ctx = MagicMock()
    mock_ctx.send = AsyncMock()
    mock_ctx.logger = MagicMock()

    msg = ChatMessage(
        timestamp=datetime.utcnow(),
        msg_id=uuid4(),
        content=[TextContent(type="text", text="shows in London")],
    )

    await handle_chat(mock_ctx, "agent1qtest123", msg)

    reply_payload = mock_ctx.send.call_args_list[1].args[1]
    reply_text = next(
        b.text for b in reply_payload.content
        if isinstance(b, TextContent)
    )

    assert "Radiohead Live" in reply_text
    assert "O2 Arena" in reply_text


@pytest.mark.asyncio
async def test_handle_chat_parse_error_returns_help(mocker):
    """If intent parsing fails, agent replies with help text gracefully."""
    mocker.patch(
        "shared.services.intent_parser.parse_intent",
        side_effect=Exception("LLM unavailable"),
    )

    from uagents_core.contrib.protocols.chat import ChatMessage, TextContent
    from agents.concierge.agent import handle_chat

    mock_ctx = MagicMock()
    mock_ctx.send = AsyncMock()
    mock_ctx.logger = MagicMock()

    msg = ChatMessage(
        timestamp=datetime.utcnow(),
        msg_id=uuid4(),
        content=[TextContent(type="text", text="hi")],
    )

    await handle_chat(mock_ctx, "agent1qtest123", msg)

    # Should still send ack + reply (not crash)
    assert mock_ctx.send.call_count >= 2
