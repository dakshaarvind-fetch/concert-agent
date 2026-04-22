"""Ticketmaster Discovery API tool — step 4 of build order."""
from langchain_core.tools import tool


@tool
async def search_ticketmaster_events(
    city: str,
    start_date: str,
    end_date: str,
    genres: list[str] | None = None,
    radius_km: int = 50,
    max_price: float | None = None,
    size: int = 20,
) -> list[dict]:
    """Search Ticketmaster for live music events matching the given filters."""
    raise NotImplementedError(
        "ticketmaster.py is not yet implemented — step 4 of the build order. "
        "Implement after Supabase is confirmed working."
    )
