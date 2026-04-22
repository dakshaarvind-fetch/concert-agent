"""
LangGraph pipeline tests — implement in step 5.

Uses mocked API responses (no real keys needed).
Run with: pytest tests/test_graph.py
"""
import pytest


@pytest.mark.asyncio
async def test_pipeline_golden_path():
    """Full pipeline with mocked Ticketmaster + Claude responses."""
    pytest.skip("Implement in step 5 — graph not yet built")


@pytest.mark.asyncio
async def test_pipeline_empty_events():
    """Pipeline handles zero Ticketmaster results gracefully (Songkick fallback)."""
    pytest.skip("Implement in step 5")


@pytest.mark.asyncio
async def test_scoring_filters_low_scores():
    """Events scoring below 75 should not appear in final_picks."""
    pytest.skip("Implement in step 8")
