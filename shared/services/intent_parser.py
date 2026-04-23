"""
Intent parser — step 6 of build order.

Parses a natural-language ChatMessage into a structured Intent using
ASI:One via langchain-openai ChatOpenAI.with_structured_output().
"""
from __future__ import annotations

from datetime import date
from functools import lru_cache

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from shared.models import Intent, SearchFilters
from shared.prompts import INTENT_PARSER_SYSTEM

ASI_BASE = "https://api.asi1.ai/v1"


@lru_cache(maxsize=1)
def _llm():
    from shared.config import settings
    return ChatOpenAI(
        model=settings.asi_model,
        base_url=ASI_BASE,
        api_key=settings.asi_api_key,
        temperature=0,
    ).with_structured_output(Intent)


async def parse_intent(text: str, sender_address: str) -> Intent:
    """Parse raw chat text into a typed Intent."""
    intent: Intent = await _llm().ainvoke([
        SystemMessage(content=INTENT_PARSER_SYSTEM),
        HumanMessage(content=f"[today: {date.today().isoformat()}]\n[agent_address: {sender_address}]\n{text}"),
    ])
    # Guarantee these are always set from context, never hallucinated
    intent.agent_address = sender_address
    if not intent.user_id:
        intent.user_id = ""
    # Search intents must always have a filters object
    if intent.type == "search" and intent.filters is None:
        intent.filters = SearchFilters()
    return intent
