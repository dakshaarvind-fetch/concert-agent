# Concert Digest Agent

Sends weekly personalised concert digest emails to subscribed users.

This is an internal Hosted agent — it is not chat-addressable by end users.
It runs on a weekly `on_interval` and is deployed separately from the
Concierge agent.

## What it does

1. Pulls all users with `digest_opt_in = true` from Supabase
2. Runs each user's taste profile through the same LangGraph pipeline
   as the Concierge
3. Formats a personalised HTML email (top picks, with reasoning per pick)
4. Sends via Resend API (or Gmail SMTP fallback)
5. Records each send in `digest_log`

## Deployment

Deploy as a **Hosted agent** on Agentverse (not Mailbox). The platform's
scheduler handles the weekly invocation — no local server required.

## Configuration

Shares `.env` with the Concierge agent. Uses `DIGEST_AGENT_SEED_PHRASE`
(separate from `AGENT_SEED_PHRASE`) so the two agents have distinct addresses.
