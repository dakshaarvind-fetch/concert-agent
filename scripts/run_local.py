"""
Run the concierge agent locally with Mailbox enabled.

Usage:
    python scripts/run_local.py

Ensure AGENT_SEED_PHRASE and AGENTVERSE_API_KEY are set in .env
The agent address will be printed — register it in Agentverse via
the Agent Inspector URL shown in the uagents runtime output.
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Python 3.10+ no longer auto-creates an event loop — uagents needs one at import time
asyncio.set_event_loop(asyncio.new_event_loop())

if __name__ == "__main__":
    # Import triggers agent construction and env validation
    from agents.concierge.agent import agent
    print(f"\nAgent address: {agent.address}")
    print("Paste this address into Agentverse → Connect Mailbox Agent\n")
    agent.run()
