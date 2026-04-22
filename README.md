# Concert Concierge Agent

Autonomous concert discovery agent on [Fetch.ai Agentverse](https://agentverse.ai).
Finds live music events that match your taste, maintains a watchlist, logs shows
you've attended, and sends weekly digest emails — all via natural-language chat
on ASI:One.

## Architecture

```
ASI:One (user) → Agentverse Marketplace → Concierge Agent (Mailbox)
                                                     │
                                          LangGraph pipeline
                                                     │
                                  ┌──────────────────┤
                                  ▼                  ▼
                           Ticketmaster           Songkick
                           Spotify (taste)
                                  │
                               Supabase
                                  │
                          Digest Agent (Hosted, weekly)
                                  │
                              Gmail / Resend
```

Two agents share one Supabase backend:
- **Concierge** (Mailbox) — handles real-time chat, runs LangGraph on demand
- **Digest** (Hosted) — runs weekly, batches emails

## Build Order

Follow these steps in sequence. Do not skip ahead.

| Step | What | Status |
|------|------|--------|
| 1 | Scaffold repo | ✅ done |
| 2 | Hello-world agent — Chat Protocol round-trip on Agentverse | ✅ done (confirm manually) |
| 3 | Supabase setup — run migrations, test with seed script | ⬜ |
| 4 | Ticketmaster tool — standalone, cached, rate-limited | ⬜ |
| 5 | LangGraph skeleton — 3-node pipeline returning structured picks | ⬜ |
| 6 | Intent parser — routes chat to 6 behaviours via structured output | ⬜ |
| 7 | Wire graph into agent handler | ⬜ |
| 8 | Scoring pipeline — pgvector embeddings + Claude reasoning | ⬜ |
| 9 | Watchlist + seen handlers | ⬜ |
| 10 | Spotify OAuth — taste seeding | ⬜ |
| 11 | Songkick fallback tool | ⬜ |
| 12 | Digest agent — email on interval | ⬜ |
| 13 | Agentverse deployment — Mailbox (Concierge) + Hosted (Digest) | ⬜ |

## Quick Start

```bash
# 1. Clone and set up environment
cp .env.example .env
# fill in AGENT_SEED_PHRASE, AGENTVERSE_API_KEY, ANTHROPIC_API_KEY at minimum

# 2. Install dependencies (uv recommended)
uv venv && source .venv/bin/activate
uv pip install -r agents/concierge/requirements.txt

# 3. Run the hello-world agent locally
python scripts/run_local.py
# → prints agent address; paste it into Agentverse → Connect Mailbox Agent

# 4. Test via ASI:One
# → open chat.asi1.ai, find "concert-concierge", send any message
# → confirm you receive the echo reply
```

## Project Structure

```
concert-concierge-agent/
├── agents/
│   ├── concierge/agent.py      # Chat Protocol handler + uAgent definition
│   └── digest/agent.py         # Weekly email agent
├── shared/
│   ├── graph.py                # LangGraph state machine
│   ├── models.py               # Pydantic v2 models for all boundaries
│   ├── config.py               # pydantic-settings env loader
│   ├── prompts.py              # versioned system prompts
│   ├── scoring.py              # embedding-based taste fit
│   ├── tools/                  # LangChain @tool wrappers
│   ├── db/                     # Supabase client, repository, migrations
│   └── services/               # rate limiter, cache, email, intent parser
├── scripts/
│   ├── run_local.py            # local dev runner
│   └── seed_test_user.py       # Supabase test data
└── tests/
    ├── test_chat_protocol.py   # ack-before-reply contract
    ├── test_graph.py           # pipeline golden path (mocked)
    └── test_tools.py           # tool unit + integration tests
```

## Key Design Decisions

- **Stateless agent, stateful DB**: no globals for persistence. Agentverse Hosted
  agents reset between invocations. Everything persistent lives in Supabase.
- **`ctx.storage` only for session ephemera**: e.g. "last 5 events shown to user X"
- **Chat Protocol compliance**: `ChatAcknowledgement` is always sent before the
  reply `ChatMessage`. The protocol requires this.
- **Structured LLM outputs only**: every Claude call uses `.with_structured_output()`.
  No ad-hoc JSON parsing.
- **`agent_address` as identity**: the sender's `agent1q...` address is the stable
  primary key in `profiles.agent_address`.

## Environment Variables

See [`.env.example`](.env.example) for the full list.

Minimum required for step 2 (hello-world):
- `AGENT_SEED_PHRASE`
- `AGENTVERSE_API_KEY`

## Tests

```bash
pytest                          # unit tests (no real API keys needed)
pytest -m integration           # integration tests (requires API keys)
```
