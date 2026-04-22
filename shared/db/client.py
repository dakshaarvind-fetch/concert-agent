"""Supabase singleton using the service-role key — step 3 of build order."""
from __future__ import annotations

import os

_client = None


def get_supabase():
    """Return a cached Supabase client.  Lazily initialised on first call."""
    global _client
    if _client is not None:
        return _client

    try:
        from supabase import create_client, Client
    except ImportError as exc:
        raise ImportError("supabase package is not installed") from exc

    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_SERVICE_KEY", "")
    if not url or not key:
        raise EnvironmentError(
            "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set before importing db.client"
        )

    _client = create_client(url, key)
    return _client
