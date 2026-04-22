-- Migration 002: Row-Level Security
-- Run after 001_schema.sql

-- Enable RLS on every user-scoped table
alter table profiles      enable row level security;
alter table taste_profiles enable row level security;
alter table watchlist      enable row level security;
alter table seen_events    enable row level security;
alter table digest_log     enable row level security;

-- events_cache is global (not user-scoped) — no RLS needed
-- but restrict mutations to service role only
alter table events_cache enable row level security;

-- Service-role key bypasses RLS — the backend always uses it.
-- The policies below apply to the anon/authenticated roles only.

-- profiles: users can only see/edit their own row
create policy "profiles: service role only"
  on profiles for all
  using (auth.role() = 'service_role');

create policy "taste_profiles: service role only"
  on taste_profiles for all
  using (auth.role() = 'service_role');

create policy "watchlist: service role only"
  on watchlist for all
  using (auth.role() = 'service_role');

create policy "seen_events: service role only"
  on seen_events for all
  using (auth.role() = 'service_role');

create policy "digest_log: service role only"
  on digest_log for all
  using (auth.role() = 'service_role');

create policy "events_cache: service role only"
  on events_cache for all
  using (auth.role() = 'service_role');
