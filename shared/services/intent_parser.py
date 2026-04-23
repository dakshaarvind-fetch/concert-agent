"""
Intent parser — step 6 of build order.

Parses a natural-language ChatMessage into a structured Intent using
ASI:One via langchain-openai ChatOpenAI.with_structured_output().
"""
from __future__ import annotations

from shared.models import Intent


async def parse_intent(text: str, sender_address: str) -> Intent:
    """
    Parse raw chat text into a typed Intent.

    Uses ChatOpenAI(base_url=ASI:One).with_structured_output(Intent) — no ad-hoc JSON parsing.
    """
    raise NotImplementedError(
        "intent_parser.parse_intent — implement in step 6. "
        "Wire ChatOpenAI(base_url=ASI_BASE, api_key=asi_api_key) with .with_structured_output(Intent) here."
    )
