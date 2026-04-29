"""
Pytest configuration — sets dummy env vars before any module is imported
so that pydantic-settings and the agent module-level guards don't crash.
"""
import os
from unittest.mock import MagicMock, patch

# Must be set before shared.config or agents.concierge.agent are imported.
os.environ.setdefault("AGENT_SEED_PHRASE", "test word one two three four five six seven eight nine ten")
os.environ.setdefault("AGENTVERSE_API_KEY", "test-agentverse-key")
os.environ.setdefault("ASI_API_KEY", "test-asi-key")
os.environ.setdefault("TICKETMASTER_API_KEY", "test-tm-key")
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test-service-key")

# Prevent the uagents Agent() constructor from attempting network connections
# when agents/concierge/agent.py is imported during test collection.
_agent_patcher = patch("uagents.Agent", return_value=MagicMock())
_agent_patcher.start()
