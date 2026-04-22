-- Migration 003: event cache maintenance function
-- Purges expired events — call periodically or hook to a pg_cron job

create or replace function purge_expired_events()
returns int
language plpgsql
security definer
as $$
declare
  deleted int;
begin
  delete from events_cache where expires_at < now();
  get diagnostics deleted = row_count;
  return deleted;
end;
$$;

-- Optional: schedule via pg_cron if your Supabase plan supports it
-- select cron.schedule('purge-event-cache', '0 * * * *', 'select purge_expired_events()');
