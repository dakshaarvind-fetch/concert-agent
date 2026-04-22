"""
Digest Agent — step 12 of build order.

A separate Hosted uAgent that runs on a weekly interval, pulls all
digest-subscribed users from Supabase, and emails personalised picks.

Deploy as a Hosted agent on Agentverse (not Mailbox) so it runs on
Agentverse's infrastructure without needing a local server.
"""
import os
import sys

from dotenv import load_dotenv
from uagents import Agent, Context

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

load_dotenv()

AGENT_SEED_PHRASE = os.getenv("DIGEST_AGENT_SEED_PHRASE") or os.getenv("AGENT_SEED_PHRASE")
if not AGENT_SEED_PHRASE:
    raise EnvironmentError("DIGEST_AGENT_SEED_PHRASE (or AGENT_SEED_PHRASE) must be set")

agent = Agent(
    name="concert-digest",
    seed=AGENT_SEED_PHRASE,
    publish_agent_details=True,
)


@agent.on_interval(period=60 * 60 * 24 * 7)  # weekly
async def send_weekly_digests(ctx: Context) -> None:
    """Fetch all digest subscribers and send personalised picks emails."""
    raise NotImplementedError(
        "send_weekly_digests — implement in step 12. "
        "Import ProfileRepo, run_concierge_pipeline, and email_sender."
    )


if __name__ == "__main__":
    print(f"Digest agent address: {agent.address}")
    agent.run()
