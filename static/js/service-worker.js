'use strict';
const CACHE = 'unisphere-static-__CACHE_VERSION__';
const PUBLIC_ASSETS = ['/offline/', '/static/css/app.css', '/static/js/app.js', '/static/icons/icon-192.png', '/static/icons/icon-512.png', '/static/icons/icon-maskable.png'];
self.addEventListener('install', event => { event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(PUBLIC_ASSETS))); });
self.addEventListener('activate', event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => key.startsWith('unisphere-') && key !== CACHE).map(key => caches.delete(key)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', event => {
  const request = event.request;
  const url = new URL(request.url);
  if (request.method !== 'GET' || url.origin !== self.location.origin) return;
  if (request.mode === 'navigate') {
    // Network only: never persist a signed-in page, login response or academic record.
    event.respondWith(fetch(request).catch(() => caches.match('/offline/')));
    return;
  }
  if (PUBLIC_ASSETS.includes(url.pathname)) {
    event.respondWith(caches.match(url.pathname).then(cached => cached || fetch(request)));
  }
  // APIs, documents, submissions and all other URLs bypass the offline cache.
});
