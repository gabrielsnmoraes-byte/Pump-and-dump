// Offline support: the app shell works without signal; data syncs when back online.
const CACHE = "pd-shell-v17";
const SHELL = ["./", "index.html", "config.js", "manifest.webmanifest", "vendor/supabase.js", "vendor/three.min.js",
  "icons/icon-180.png", "icons/icon-192.png", "icons/icon-512.png"];
self.addEventListener("install", e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())); });
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", e => {
  const req = e.request; if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.hostname.endsWith("supabase.co")) return;              // never cache account data
  const isFont = /fonts\.(googleapis|gstatic)\.com$/.test(url.hostname);
  if (url.origin !== location.origin && !isFont) return;
  if (req.mode === "navigate" || /\.(html|js|webmanifest)$/.test(url.pathname) || url.pathname.endsWith("/")) {
    // network first so updates arrive; cache as fallback offline
    const fresh = url.origin === location.origin ? fetch(url.href, { cache: "no-cache", credentials: "same-origin" }) : fetch(req);
    e.respondWith(fresh.then(r => { const c = r.clone(); caches.open(CACHE).then(k => k.put(req, c)); return r; })
      .catch(() => caches.match(req).then(r => r || caches.match("index.html"))));
    return;
  }
  e.respondWith(caches.match(req).then(hit => hit || fetch(req).then(r => {
    if (r.ok || r.type === "opaque") { const c = r.clone(); caches.open(CACHE).then(k => k.put(req, c)); }
    return r;
  })));
});
