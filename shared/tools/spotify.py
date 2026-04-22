"""Spotify Web API tool for taste seeding — step 10 of build order."""
from langchain_core.tools import tool


@tool
async def fetch_spotify_taste(user_id: str, access_token: str) -> dict:
    """
    Pull the user's top artists and top tracks from Spotify and return
    a taste dict for embedding + storage in taste_profiles.
    """
    raise NotImplementedError(
        "spotify.py is not yet implemented — step 10 of the build order."
    )
