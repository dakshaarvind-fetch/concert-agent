"""
Chat Protocol roundtrip test — implement in step 2 verification.

Confirms: ChatMessage in → ChatAcknowledgement first → ChatMessage reply.
"""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4


@pytest.mark.asyncio
async def test_handle_chat_sends_ack_before_reply():
    """
    Ensures the handler sends ChatAcknowledgement before the reply ChatMessage.
    This is a Chat Protocol hard requirement.
    """
    from uagents_core.contrib.protocols.chat import (
        ChatMessage,
        TextContent,
    )
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

    from uagents_core.contrib.protocols.chat import ChatAcknowledgement
    first_payload = calls[0].args[1]
    assert isinstance(first_payload, ChatAcknowledgement), (
        f"First send must be ChatAcknowledgement, got {type(first_payload)}"
    )

    second_payload = calls[1].args[1]
    assert isinstance(second_payload, ChatMessage), (
        f"Second send must be ChatMessage reply, got {type(second_payload)}"
    )


@pytest.mark.asyncio
async def test_handle_chat_ignores_empty_content():
    """Handler with no TextContent blocks should not send a reply."""
    from uagents_core.contrib.protocols.chat import ChatMessage
    from agents.concierge.agent import handle_chat

    mock_ctx = MagicMock()
    mock_ctx.send = AsyncMock()
    mock_ctx.logger = MagicMock()

    msg = ChatMessage(
        timestamp=datetime.utcnow(),
        msg_id=uuid4(),
        content=[],  # no TextContent
    )

    await handle_chat(mock_ctx, "agent1qtest123", msg)

    calls = mock_ctx.send.call_args_list
    # Only the ack should have been sent, no reply
    assert len(calls) == 1, "Should only send ack when there's no text content"
