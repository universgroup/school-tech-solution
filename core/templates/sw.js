const CACHE_NAME = 'STS-V1';
const urlsToCache = [
  '/',
  '/static/assets/dist/css/adminlte.min.css',
  '/static/assets/dist/js/adminlte.min.js',
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(response => response || fetch(event.request))
  );
});