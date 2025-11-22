// Jednostavan service worker: keš statike + offline fallback
const CACHE_VERSION = "v1";
const STATIC_CACHE = `static-${CACHE_VERSION}`;
const APP_SHELL = [
  "/",
  "/static/manifest.json",
  "/static/offline.html",
  // Dodaj po želji tvoje CSS/JS datoteke: npr.
  // "/static/css/main.css",
  // "/static/js/app.js",
];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(STATIC_CACHE).then((c) => c.addAll(APP_SHELL)));
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== STATIC_CACHE).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  const accept = req.headers.get("accept") || "";
  const wantsHTML = accept.includes("text/html");

  event.respondWith(
    fetch(req)
      .then((res) => {
        // “Keširaj u hodu” GET zahtjeve s iste domene
        if (req.method === "GET" && new URL(req.url).origin === location.origin) {
          const copy = res.clone();
          caches.open(STATIC_CACHE).then((c) => c.put(req, copy)).catch(() => {});
        }
        return res;
      })
      .catch(async () => {
        // Offline: probaj iz keša; za HTML daj offline stranicu
        const cached = await caches.match(req);
        if (cached) return cached;
        if (wantsHTML) return caches.match("/static/offline.html");
        return new Response("", { status: 504, statusText: "Offline" });
      })
  );
});
