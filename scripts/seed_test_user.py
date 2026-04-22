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


async def main() -> None:
    raise NotImplementedError(
        "seed_test_user.py — implement in step 3 once migrations are run. "
        "Insert a row into profiles + taste_profiles."
    )


if __name__ == "__main__":
    asyncio.run(main())
