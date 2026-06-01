const CACHE_NAME = 'salon-kim-hien-v1';
const ASSETS = [
  '/',
  '/app_cua_ni' // Tùy thuộc vào đường dẫn của ní, nếu là app chính thì thường là '/'
];

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS)));
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});
