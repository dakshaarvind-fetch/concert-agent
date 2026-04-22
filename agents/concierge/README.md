# Concert Concierge

Finds live music events you'll actually love, based on your taste.

## What this agent does

Given a city and your music preferences, it searches live concerts and festivals
across Ticketmaster and Songkick, scores each one for how well it fits your
personal taste using your Spotify listening history, and returns the best matches
with venues, dates, and ticket links.

Ratings you give to shows you attend are fed back into future recommendations —
the more you use it, the sharper your picks become.

## How to use it

Send a chat message like:

- "Find me indie shows in Brooklyn next month under $80"
- "Any techno events in Berlin this weekend?"
- "What's on in London in June — I'm into ambient and post-rock"
- "Save the LCD Soundsystem show to my watchlist"
- "I went to the Fred Again show last night, 5 stars, energy was insane"
- "Update my city to Los Angeles"
- "Unsubscribe from weekly digest emails"

## Features

- **Taste-based event matching** — events scored 0–100 against your listening
  history using vector embeddings; only the best picks are surfaced
- **Watchlist** — save shows you're considering; get notified on price drops
- **Attended-show log** — rate shows 1–5 stars; ratings sharpen future picks
- **Weekly digest email** — new shows matching your taste, delivered to your inbox
- **Worldwide coverage** — Ticketmaster (primary) + Songkick (fallback for
  international and underground venues)

## Supported cities

Any city covered by Ticketmaster or Songkick. Just say the city name — the agent
handles geocoding and radius search.

## Privacy

Your Spotify data is only used to compute a taste embedding stored in our database.
Raw listening history is never stored. Agent communication is end-to-end encrypted
via the Fetch.ai network.

## Tech

Built with uAgents + LangGraph + Claude (Anthropic). Persists state in Supabase.
Discoverable on ASI:One via the Chat Protocol.
