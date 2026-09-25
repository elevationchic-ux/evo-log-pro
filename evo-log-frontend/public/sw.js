/* EVO-LOG - Service Worker
 *
 * Perimetre honnete : ce sw met en cache la coquille statique de l'app et
 * sert une page /offline quand le reseau lache. Il ne simule JAMAIS des
 * donnees : les appels /api/* ne sont jamais interceptes ni mises en cache
 * (la revalidation des donnees metier passe par l'outbox IndexedDB de
 * src/utils/offlineSync.ts, avec le token de session).
 */

const VERSION = 'evo-log-v1';
const STATIC_CACHE = `${VERSION}-static`;
const PAGE_CACHE = `${VERSION}-pages`;

const PRECACHE_URLS = ['/offline', '/manifest.json'];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches
      .open(STATIC_CACHE)
      .then((cache) => cache.addAll(PRECACHE_URLS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(keys.filter((k) => !k.startsWith(VERSION)).map((k) => caches.delete(k)))
      )
      .then(() => self.clients.claim())
  );
});

function isStaticAsset(url) {
  return (
    url.origin === self.location.origin &&
    (url.pathname.startsWith('/_next/static/') ||
      url.pathname.startsWith('/icons/') ||
      url.pathname.startsWith('/images/') ||
      /\.(css|js|woff2?|png|jpe?g|svg|webp|ico)$/i.test(url.pathname))
  );
}

function isApiCall(url) {
  // API distante (Railway) ou locale : ne jamais toucher aux requetes metier.
  return url.origin !== self.location.origin || url.pathname.startsWith('/api');
}

self.addEventListener('fetch', (event) => {
  const { request } = event;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);

  // API : on laisse passer sans cache (pas de fausse donnee "fraiche").
  if (isApiCall(url)) return;

  // Assets statiques hashes : cache-first (ils sont immuables).
  if (isStaticAsset(url)) {
    event.respondWith(
      caches.match(request).then(
        (cached) =>
          cached ||
          fetch(request).then((res) => {
            if (res.ok) {
              const clone = res.clone();
              caches.open(STATIC_CACHE).then((cache) => cache.put(request, clone));
            }
            return res;
          })
      )
    );
    return;
  }

  // Navigations : reseau d'abord (donnees live), cache puis page offline.
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request)
        .then((res) => {
          if (res.ok) {
            const clone = res.clone();
            caches.open(PAGE_CACHE).then((cache) => cache.put(request, clone));
          }
          return res;
        })
        .catch(() =>
          caches.match(request).then(
            (cached) => cached || caches.match('/offline').then((page) => page || Response.error())
          )
        )
    );
  }
  // Autres memes-origines : comportement par defaut (pas de cache frauduleux).
});
