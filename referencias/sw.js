// Service Worker de la Ficha D&D 2024 - primero red, cache como respaldo offline.
// _assemble.py sustituye el sufijo de CACHE_NAME por un hash del build: cada despliegue
// cambia este fichero, el navegador instala el SW nuevo y se borran las caches viejas.
const CACHE_NAME = 'ficha-dnd-2024-__BUILD__';
const PRECACHE = ['./', './index.html', './manifest.json'];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(PRECACHE.map((u) => new Request(u, { cache: 'reload' }))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== self.location.origin) return;
  const navegacion = req.mode === 'navigate';
  event.respondWith(
    // la pagina se revalida siempre contra el servidor (sin cache HTTP intermedia)
    fetch(navegacion ? new Request(req.url, { cache: 'no-cache', credentials: 'same-origin' }) : req)
      .then((resp) => {
        if (resp && resp.ok && resp.type === 'basic') {
          const copia = resp.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(req.url, copia));
        }
        return resp;
      })
      .catch(async () => {
        // sin red: lo ultimo que se guardo (y para la pagina, en ultimo caso index.html)
        const cached = await caches.match(req.url, { ignoreSearch: true });
        if (cached) return cached;
        if (navegacion) {
          const idx = await caches.match('./index.html');
          if (idx) return idx;
        }
        return Response.error();
      })
  );
});
