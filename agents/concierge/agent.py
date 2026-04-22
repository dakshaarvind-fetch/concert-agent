"""
Concert Concierge — Agentverse Mailbox Agent (step 2: hello-world)

This is the minimal Chat Protocol implementation.  Every ChatMessage gets:
  1. An immediate ChatAcknowledgement (protocol requirement).
  2. A TextContent reply echoing the received text back.

Nothing downstream (LangGraph, Supabase, Ticketmaster) is wired yet.
Confirm the round-trip on ASI:One before extending.
"""
import os
import sys
from datetime import datetime
from uuid import uuid4

from dotenv import load_dotenv
from uagents import Agent, Context, Protocol
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    EndSessionContent,
    StartSessionContent,
    TextContent,
    chat_protocol_spec,
)

# Allow running from the repo root: `python agents/concierge/agent.py`
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

load_dotenv()

AGENT_SEED_PHRASE = os.getenv("AGENT_SEED_PHRASE")
AGENTVERSE_API_KEY = os.getenv("AGENTVERSE_API_KEY")

if not AGENT_SEED_PHRASE:
    raise EnvironmentError(
        "AGENT_SEED_PHRASE is not set. "
        "Copy .env.example → .env and fill in a 12-word seed phrase."
    )
if not AGENTVERSE_API_KEY:
    raise EnvironmentError(
        "AGENTVERSE_API_KEY is not set. "
        "Get one from agentverse.ai → Profile → API Keys."
    )

agent = Agent(
    name="concert-concierge",
    seed=AGENT_SEED_PHRASE,
    port=8001,
    mailbox=True,               # Agentverse Mailbox — required for hosted deployment
    publish_agent_details=True, # makes the agent discoverable in the Marketplace
)

chat_proto = Protocol(spec=chat_protocol_spec)


@chat_proto.on_message(ChatMessage)
async def handle_chat(ctx: Context, sender: str, msg: ChatMessage) -> None:
    ctx.logger.info(f"[handle_chat] msg_id={msg.msg_id} sender={sender}")

    # 1) Chat Protocol requirement: acknowledge before replying
    await ctx.send(
        sender,
        ChatAcknowledgement(
            timestamp=datetime.utcnow(),
            acknowledged_msg_id=msg.msg_id,
        ),
    )

    # 2) Extract text from content blocks
    text = next(
        (block.text for block in msg.content if isinstance(block, TextContent)),
        None,
    )
    if not text:
        ctx.logger.warning("[handle_chat] no TextContent in message — ignoring")
        return

    ctx.logger.info(f"[handle_chat] user text: {text!r}")

    # 3) Hello-world reply — confirms the round-trip works
    reply = (
        f"Concert Concierge here! I received your message: \"{text}\"\n\n"
        "I'm not yet connected to the full pipeline — this confirms the "
        "Chat Protocol round-trip is working. Stay tuned for concert picks!"
    )
    await _send_text(ctx, sender, reply)


@chat_proto.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement) -> None:
    ctx.logger.info(f"[handle_ack] ack for msg_id={msg.acknowledged_msg_id} from {sender}")


async def _send_text(ctx: Context, to: str, text: str, end: bool = False) -> None:
    """Helper: sends a ChatMessage with a single TextContent block."""
    content: list = [TextContent(type="text", text=text)]
    if end:
        content.append(EndSessionContent(type="end-session"))
    await ctx.send(
        to,
        ChatMessage(
            timestamp=datetime.utcnow(),
            msg_id=uuid4(),
            content=content,
        ),
    )


# Include the protocol — publish_manifest=True registers the spec with Agentverse
agent.include(chat_proto, publish_manifest=True)

if __name__ == "__main__":
    print(f"Agent address: {agent.address}")
    agent.run()
