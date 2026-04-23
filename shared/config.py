"""Central configuration — loaded once at import time via pydantic-settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── uAgents ──────────────────────────────────────────────────────────────
    agent_seed_phrase: str
    agentverse_api_key: str

    # ── LLM ──────────────────────────────────────────────────────────────────
    asi_api_key: str                     # ASI:One — chat completions + embeddings
    asi_model: str = "asi1"              # model name served at ASI:One endpoint

    # ── Event APIs ───────────────────────────────────────────────────────────
    ticketmaster_api_key: str
    eventbrite_api_key: str = ""        # optional — indie/smaller venue fallback

    # ── Database ─────────────────────────────────────────────────────────────
    supabase_url: str
    supabase_service_key: str

    # ── Email ────────────────────────────────────────────────────────────────
    gmail_smtp_user: str = ""
    gmail_smtp_app_password: str = ""
    resend_api_key: str = ""

    # ── Observability ────────────────────────────────────────────────────────
    langchain_api_key: str = ""
    langchain_tracing_v2: str = "false"
    langchain_project: str = "concert-concierge"


settings = Settings()
