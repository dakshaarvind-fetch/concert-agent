"""
Concert Concierge — Agentverse Mailbox Agent (step 7: full pipeline wired)

Flow per ChatMessage:
  1. ChatAcknowledgement (protocol requirement)
  2. parse_intent → route to handler → send reply
"""
import os
import sys
from datetime import datetime, timezone
from uuid import uuid4

from dotenv import load_dotenv
from uagents import Agent, Context, Protocol
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    EndSessionContent,
    TextContent,
    chat_protocol_spec,
)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

load_dotenv()

AGENT_SEED_PHRASE = os.getenv("AGENT_SEED_PHRASE")
AGENTVERSE_API_KEY = os.getenv("AGENTVERSE_API_KEY")

if not AGENT_SEED_PHRASE:
    raise EnvironmentError(
        "AGENT_SEED_PHRASE is not set. Copy .env.example → .env and fill in a 12-word seed phrase."
    )
if not AGENTVERSE_API_KEY:
    raise EnvironmentError(
        "AGENTVERSE_API_KEY is not set. Get one from agentverse.ai → Profile → API Keys."
    )

agent = Agent(
    name="concert-concierge",
    seed=AGENT_SEED_PHRASE,
    port=8001,
    mailbox=True,
    publish_agent_details=True,
)

chat_proto = Protocol(spec=chat_protocol_spec)


# ── Main handler ──────────────────────────────────────────────────────────────

@chat_proto.on_message(ChatMessage)
async def handle_chat(ctx: Context, sender: str, msg: ChatMessage) -> None:
    ctx.logger.info(f"[handle_chat] msg_id={msg.msg_id} sender={sender}")

    # 1. Ack first — Chat Protocol hard requirement
    await ctx.send(
        sender,
        ChatAcknowledgement(
            timestamp=datetime.now(timezone.utc),
            acknowledged_msg_id=msg.msg_id,
        ),
    )

    # 2. Extract text
    text = next(
        (block.text for block in msg.content if isinstance(block, TextContent)),
        None,
    )
    if not text:
        ctx.logger.warning("[handle_chat] no TextContent — ignoring")
        return

    ctx.logger.info(f"[handle_chat] text={text!r}")

    # 3. Parse intent
    try:
        from shared.services.intent_parser import parse_intent
        intent = await parse_intent(text, sender)
    except Exception as exc:
        ctx.logger.error(f"[handle_chat] intent parsing failed: {exc}")
        from shared.prompts import HELP_TEXT
        await _send_text(ctx, sender, HELP_TEXT, end=True)
        return

    ctx.logger.info(f"[handle_chat] intent={intent.type}")

    # 4. Route
    try:
        reply = await _route(intent, ctx)
    except Exception as exc:
        ctx.logger.error(f"[handle_chat] routing failed: {exc}")
        reply = "Something went wrong processing your request. Please try again."

    await _send_text(ctx, sender, reply, end=True)


@chat_proto.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement) -> None:
    ctx.logger.info(f"[handle_ack] ack for {msg.acknowledged_msg_id} from {sender}")


# ── Intent router ─────────────────────────────────────────────────────────────

async def _route(intent, ctx: Context) -> str:
    if intent.type == "search":
        return await _handle_search(intent, ctx)
    elif intent.type == "help":
        from shared.prompts import HELP_TEXT
        return HELP_TEXT
    elif intent.type in ("add_watchlist", "remove_watchlist", "log_seen", "update_profile"):
        return (
            f"Got it — {intent.type.replace('_', ' ')} is coming in the next update! "
            "Try searching for events in the meantime."
        )
    else:
        from shared.prompts import HELP_TEXT
        return HELP_TEXT


async def _handle_search(intent, ctx: Context) -> str:
    from shared.graph import run_concierge_pipeline
    from shared.models import SearchFilters

    filters = intent.filters or SearchFilters()
    ctx.logger.info(f"[search] city={filters.city} genres={filters.genres}")

    picks = await run_concierge_pipeline(
        agent_address=intent.agent_address,
        filters=filters,
        query=intent.raw_query,
        user_id=intent.user_id,
    )

    if not picks:
        city_str = f" in {filters.city}" if filters.city else ""
        return (
            f"No events found{city_str} matching your search. "
            "Try a wider date range, different city, or drop the genre filter."
        )

    return _format_picks(picks, filters)


def _format_picks(picks: list[dict], filters) -> str:
    city = (filters.city or "").title()
    header = f"Found {len(picks)} concert{'s' if len(picks) != 1 else ''}{' in ' + city if city else ''}:\n\n"

    lines = []
    for i, event in enumerate(picks, 1):
        venue = event.get("venue") or {}
        name = event.get("name", "Unknown Event")
        venue_name = venue.get("name", "Venue TBC")

        # Date formatting
        starts = event.get("starts_at", "")
        if starts:
            try:
                dt = datetime.fromisoformat(starts.replace("Z", "+00:00"))
                date_str = dt.strftime("%d %b %Y, %H:%M")
            except ValueError:
                date_str = starts[:10]
        else:
            date_str = "Date TBC"

        # Price
        price_min = event.get("price_min")
        price_max = event.get("price_max")
        if price_min is not None:
            if price_max and price_max != price_min:
                price_str = f"  |  £{price_min:.0f}–{price_max:.0f}"
            else:
                price_str = f"  |  £{price_min:.0f}"
        else:
            price_str = ""

        ticket_str = f"\n   {event['ticket_url']}" if event.get("ticket_url") else ""

        lines.append(f"{i}. {name} — {venue_name}")
        lines.append(f"   {date_str}{price_str}{ticket_str}")

    return header + "\n".join(lines)


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _send_text(ctx: Context, to: str, text: str, end: bool = False) -> None:
    content: list = [TextContent(type="text", text=text)]
    if end:
        content.append(EndSessionContent(type="end-session"))
    await ctx.send(
        to,
        ChatMessage(
            timestamp=datetime.now(timezone.utc),
            msg_id=uuid4(),
            content=content,
        ),
    )


agent.include(chat_proto, publish_manifest=True)

if __name__ == "__main__":
    print(f"Agent address: {agent.address}")
    agent.run()
