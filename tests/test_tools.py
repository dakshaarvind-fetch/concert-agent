"""
Tool-level tests — implement in step 4.

Run integration tests with: pytest -m integration tests/test_tools.py
"""
import pytest


@pytest.mark.asyncio
async def test_ticketmaster_returns_events(mocker):
    """Mock HTTP — confirms tool parses response into EventRaw list."""
    pytest.skip("Implement in step 4 — tool not yet built")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_ticketmaster_real_api():
    """Hits real Ticketmaster API. Requires TICKETMASTER_API_KEY."""
    pytest.skip("Implement in step 4 — set TICKETMASTER_API_KEY and remove skip")


@pytest.mark.asyncio
async def test_rate_limiter_does_not_exceed_5rps():
    """Token bucket should not allow more than 5 requests per second."""
    import asyncio
    import time
    from shared.services.rate_limiter import TokenBucket

    bucket = TokenBucket(rate=5.0, capacity=5.0)
    start = time.monotonic()
    for _ in range(6):
        await bucket.acquire()
    elapsed = time.monotonic() - start
    # 6 requests at 5/s should take at least 0.2s (1 extra token wait)
    assert elapsed >= 0.19, f"Rate limiter too fast: {elapsed:.3f}s for 6 requests"
