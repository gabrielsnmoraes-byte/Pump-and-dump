-- Pump & Dump database setup. Run once in Supabase: SQL Editor > New query > paste > Run.

create table if not exists public.profiles (
  user_id    uuid primary key default auth.uid() references auth.users(id) on delete cascade,
  data       jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

create table if not exists public.workouts (
  user_id    uuid not null default auth.uid() references auth.users(id) on delete cascade,
  id         text not null,
  date       timestamptz not null,
  data       jsonb not null,
  created_at timestamptz not null default now(),
  primary key (user_id, id)
);
create index if not exists workouts_user_date on public.workouts (user_id, date desc);

-- Each person can only see and change their own rows.
alter table public.profiles enable row level security;
alter table public.workouts enable row level security;

drop policy if exists "own profile" on public.profiles;
create policy "own profile" on public.profiles for all to authenticated
  using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);

drop policy if exists "own workouts" on public.workouts;
create policy "own workouts" on public.workouts for all to authenticated
  using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
