"""
Seed a test user and taste profile in Supabase.

Usage:
    python scripts/seed_test_user.py

Requires SUPABASE_URL and SUPABASE_SERVICE_KEY in .env
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv

load_dotenv()

TEST_AGENT_ADDRESS = "agent1qtestconcertconcierge000000000000000000000000000000000000"

TEST_PROFILE = {
    "agent_address": TEST_AGENT_ADDRESS,
    "email": "test@example.com",
    "location_city": "London",
    "search_radius_km": 30,
    "digest_opt_in": True,
}

TEST_TASTE = {
    "favourite_artists": ["Radiohead", "Four Tet", "Jon Hopkins"],
    "favourite_genres": ["electronic", "ambient", "indie"],
    "vibe_descriptors": ["intimate", "atmospheric", "late night"],
}


async def main() -> None:
    from supabase import create_client

    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_SERVICE_KEY", "")
    if not url or not key:
        raise EnvironmentError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env")

    db = create_client(url, key)

    # Upsert profile
    result = db.table("profiles").upsert(TEST_PROFILE, on_conflict="agent_address").execute()
    profile = result.data[0]
    user_id = profile["id"]
    print(f"Profile upserted — id: {user_id}, city: {profile['location_city']}")

    # Upsert taste profile
    db.table("taste_profiles").upsert(
        {"user_id": user_id, **TEST_TASTE},
        on_conflict="user_id",
    ).execute()
    print(f"Taste profile upserted — artists: {TEST_TASTE['favourite_artists']}")

    # Verify round-trip
    taste = db.table("taste_profiles").select("*").eq("user_id", user_id).single().execute()
    assert taste.data["favourite_genres"] == TEST_TASTE["favourite_genres"], "Round-trip mismatch"

    print("\nSupabase connection verified. Tables are ready.")
    print(f"Test user_id: {user_id}")


if __name__ == "__main__":
    asyncio.run(main())
