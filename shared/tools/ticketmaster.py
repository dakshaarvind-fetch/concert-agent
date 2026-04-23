"""Ticketmaster Discovery API tool — step 4 of build order."""
from __future__ import annotations

import httpx
from langchain_core.tools import tool

from shared.config import settings
from shared.services.event_cache import cache_events, get_cached_events
from shared.services.rate_limiter import ticketmaster_bucket

TM_BASE = "https://app.ticketmaster.com/discovery/v2"


def _to_tm_datetime(date_str: str) -> str:
    """Ensure date string is in Ticketmaster's required ISO 8601 format."""
    if "T" not in date_str:
        return f"{date_str}T00:00:00Z"
    return date_str if date_str.endswith("Z") else date_str + "Z"


def _best_image(images: list[dict]) -> str | None:
    candidates = [i for i in images if i.get("ratio") == "16_9"] or images
    return max(candidates, key=lambda i: i.get("width", 0)).get("url") if candidates else None


def _normalise(event: dict) -> dict:
    embedded = event.get("_embedded", {})

    v = (embedded.get("venues") or [{}])[0]
    loc = v.get("location", {})
    venue = {
        "name": v.get("name", "Unknown Venue"),
        "address": v.get("address", {}).get("line1"),
        "city": v.get("city", {}).get("name"),
        "country": v.get("country", {}).get("name"),
        "lat": float(loc["latitude"]) if loc.get("latitude") else None,
        "lng": float(loc["longitude"]) if loc.get("longitude") else None,
    }

    artists = [a["name"] for a in embedded.get("attractions", []) if "name" in a]

    genres: list[str] = []
    for c in event.get("classifications", []):
        for key in ("genre", "subGenre"):
            name = c.get(key, {}).get("name")
            if name and name != "Undefined":
                genres.append(name)
    genres = list(dict.fromkeys(genres))  # deduplicate, preserve order

    price_ranges = event.get("priceRanges", [])
    price_min = min((p["min"] for p in price_ranges if "min" in p), default=None)
    price_max = max((p["max"] for p in price_ranges if "max" in p), default=None)

    city_name = venue["city"]
    return {
        "id": event["id"],
        "source": "ticketmaster",
        "name": event["name"],
        "artists": artists,
        "venue": venue,
        "city": city_name.lower() if city_name else None,
        "country": venue["country"],
        "lat": venue["lat"],
        "lng": venue["lng"],
        "starts_at": event.get("dates", {}).get("start", {}).get("dateTime"),
        "price_min": price_min,
        "price_max": price_max,
        "ticket_url": event.get("url"),
        "image_url": _best_image(event.get("images", [])),
        "genres": genres,
        "description": None,
    }


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
    # 1. Cache check
    cached = await get_cached_events(city, start_date, end_date)
    if cached is not None:
        if max_price is not None:
            cached = [e for e in cached if e.get("price_min") is None or e["price_min"] <= max_price]
        return cached[:size]

    # 2. Call Ticketmaster Discovery API
    params: dict = {
        "apikey": settings.ticketmaster_api_key,
        "city": city,
        "classificationName": "Music",
        "startDateTime": _to_tm_datetime(start_date),
        "endDateTime": _to_tm_datetime(end_date),
        "radius": radius_km,
        "unit": "km",
        "size": min(size, 200),
        "sort": "date,asc",
    }
    if genres:
        params["keyword"] = " ".join(genres)

    await ticketmaster_bucket.acquire()
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{TM_BASE}/events.json", params=params)
        resp.raise_for_status()

    raw_events = resp.json().get("_embedded", {}).get("events", [])

    # 3. Normalise → cache → filter → return
    events = [_normalise(e) for e in raw_events]
    await cache_events(events)

    if max_price is not None:
        events = [e for e in events if e.get("price_min") is None or e["price_min"] <= max_price]

    return events[:size]
