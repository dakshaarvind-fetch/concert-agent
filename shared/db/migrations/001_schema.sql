-- Migration 001: core schema
-- Run in Supabase SQL Editor (step 3 of build order)

create extension if not exists vector;

-- ── profiles ─────────────────────────────────────────────────────────────────
create table if not exists profiles (
  id                uuid        primary key default gen_random_uuid(),
  agent_address     text        unique not null,   -- uAgent address, primary identity
  email             text,
  location_city     text,
  location_lat      numeric,
  location_lng      numeric,
  search_radius_km  int         not null default 50,
  digest_opt_in     boolean     not null default true,
  created_at        timestamptz not null default now(),
  updated_at        timestamptz not null default now()
);

-- ── taste_profiles ────────────────────────────────────────────────────────────
create table if not exists taste_profiles (
  user_id            uuid        primary key references profiles(id) on delete cascade,
  favourite_artists  jsonb       not null default '[]'::jsonb,
  favourite_genres   jsonb       not null default '[]'::jsonb,
  vibe_descriptors   text[]      not null default '{}',
  artist_embedding   vector(1536),                  -- aggregated via text-embedding-3-small
  updated_at         timestamptz not null default now()
);

-- ── events_cache ──────────────────────────────────────────────────────────────
create table if not exists events_cache (
  id          text        primary key,              -- ticketmaster/songkick id
  source      text        not null,
  name        text        not null,
  artists     jsonb       not null default '[]'::jsonb,
  venue       jsonb       not null default '{}'::jsonb,
  city        text,
  country     text,
  lat         numeric,
  lng         numeric,
  starts_at   timestamptz,
  price_min   numeric,
  price_max   numeric,
  ticket_url  text,
  image_url   text,
  raw         jsonb,
  fetched_at  timestamptz not null default now(),
  expires_at  timestamptz not null default (now() + interval '24 hours')
);

create index if not exists events_cache_city_starts_at on events_cache (city, starts_at);
create index if not exists events_cache_expires_at     on events_cache (expires_at);

-- ── watchlist ─────────────────────────────────────────────────────────────────
create table if not exists watchlist (
  id                    uuid        primary key default gen_random_uuid(),
  user_id               uuid        not null references profiles(id) on delete cascade,
  event_id              text        not null references events_cache(id),
  added_at              timestamptz not null default now(),
  target_price          numeric,
  notify_on_price_drop  boolean     not null default true,
  unique (user_id, event_id)
);

-- ── seen_events ───────────────────────────────────────────────────────────────
create table if not exists seen_events (
  id          uuid        primary key default gen_random_uuid(),
  user_id     uuid        not null references profiles(id) on delete cascade,
  event_id    text        not null references events_cache(id),
  attended    boolean     not null default false,
  rating      smallint    check (rating between 1 and 5),
  notes       text,
  attended_at date,
  created_at  timestamptz not null default now(),
  unique (user_id, event_id)
);

-- ── digest_log ────────────────────────────────────────────────────────────────
create table if not exists digest_log (
  id          uuid        primary key default gen_random_uuid(),
  user_id     uuid        not null references profiles(id) on delete cascade,
  sent_at     timestamptz not null default now(),
  event_count int,
  status      text
);

-- auto-update updated_at on profiles
create or replace function update_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create trigger profiles_updated_at
  before update on profiles
  for each row execute function update_updated_at();

create trigger taste_profiles_updated_at
  before update on taste_profiles
  for each row execute function update_updated_at();
