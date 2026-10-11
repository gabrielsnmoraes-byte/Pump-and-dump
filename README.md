# Pump & Dump

A workout log that installs on your phone's home screen. Log lifts, timed holds and cardio, build routines, and track PRs and progress charts. Each person signs in with their own account and sees only their own data.

Live at: https://gabrielsnmoraes-byte.github.io/pump-and-dump/

## How it's built
- Plain HTML and JavaScript, hosted free on GitHub Pages
- Accounts and sync: Supabase (email and password)
- Works offline: workouts are kept on the phone and sync when signal returns

## Setup (one time)
1. Create a free project at supabase.com.
2. In the project, open **SQL Editor**, paste `schema.sql`, and run it.
3. Copy the **Project URL** and **anon public key** (Project Settings > API) into `config.js`.
4. In **Authentication > URL Configuration**, set Site URL to the live address above.
