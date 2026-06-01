const CACHE_NAME = 'salon-kim-hien-v1';

// Những thứ ní nên cache: file icon, logo, css tĩnh
const ASSETS = [
  '/', 
  '/index.html',
  '/favicon.ico' 
];

self.addEventListener('install', (event) => {
  self.skipWaiting(); // Ép buộc cài đặt ngay không chờ đợi
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS)));
});

self.addEventListener('fetch', (event) => {
  // Chiến lược: Thử lấy từ mạng trước, nếu không có mạng thì mới dùng cache
  event.respondWith(
    fetch(event.request).catch(() => {
      return caches.match(event.request);
    })
  );
});
