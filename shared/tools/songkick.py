"""Songkick fallback tool — step 11 of build order."""
from langchain_core.tools import tool


@tool
async def search_songkick_events(
    city: str,
    start_date: str,
    end_date: str,
    size: int = 20,
) -> list[dict]:
    """Search Songkick for live music events. Used as fallback when Ticketmaster returns < 5 results."""
    raise NotImplementedError(
        "songkick.py is not yet implemented — step 11 of the build order."
    )
