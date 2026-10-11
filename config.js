// Supabase connection for Pump & Dump.
// The anon key is designed to be public: row-level security in schema.sql
// makes sure each signed-in person can only read and write their own data.
window.PD_CONFIG = {
  url: "YOUR_SUPABASE_URL",
  anonKey: "YOUR_SUPABASE_ANON_KEY"
};
