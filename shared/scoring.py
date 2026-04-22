"""Embedding-based taste fit scoring — step 8 of build order."""
from __future__ import annotations

from shared.models import EventEnriched, EventScored, TasteProfile


async def score_events(
    events: list[EventEnriched],
    taste: TasteProfile,
    user_embedding: list[float],
) -> list[EventScored]:
    """
    Score each event 0-100 based on:
    - cosine similarity of event embedding vs user taste embedding
    - explicit genre overlap
    - vibe descriptor matching

    Only events scoring >= 75 are considered picks.
    """
    raise NotImplementedError(
        "scoring.score_events — implement in step 8. "
        "Use OpenAIEmbeddings(base_url=ASI_BASE, api_key=asi_api_key) for embeddings."
    )


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Pure-Python cosine similarity. Replace with numpy for production."""
    if len(a) != len(b):
        raise ValueError(f"Vector length mismatch: {len(a)} vs {len(b)}")
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = sum(x * x for x in a) ** 0.5
    mag_b = sum(y * y for y in b) ** 0.5
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)
