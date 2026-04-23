"""Eventbrite fallback tool — step 11 of build order."""
from langchain_core.tools import tool


@tool
async def search_eventbrite_events(
    city: str,
    start_date: str,        # ISO 8601: YYYY-MM-DDTHH:MM:SS
    end_date: str,          # ISO 8601: YYYY-MM-DDTHH:MM:SS
    genres: list[str] | None = None,
    radius_km: int = 50,
    size: int = 20,
) -> list[dict]:
    """
    Search Eventbrite for live music events. Used as fallback when
    Ticketmaster returns < 5 results — strong coverage for indie/smaller venues.

    API: GET https://www.eventbriteapi.com/v3/events/search/
         Authorization: Bearer <EVENTBRITE_API_KEY>
         Params: location.address, location.within, start_date.range_start,
                 start_date.range_end, categories=103 (music), expand=venue

    Returns raw Eventbrite event dicts; caller normalises to EventRaw.
    """
    raise NotImplementedError(
        "eventbrite.py is not yet implemented — step 11 of the build order. "
        "Use httpx with Bearer auth and settings.eventbrite_api_key."
    )
