-- Migration 004: add genres and description to events_cache
alter table events_cache
  add column if not exists genres      jsonb not null default '[]'::jsonb,
  add column if not exists description text;
