const CACHE_NAME = 'salon-kim-hien-v2';

// 1. Chỉ cache những file "bất biến" để App mở lên được khi mất mạng
const ASSETS = [
  '/', 
  '/index.html'
];

// Cài đặt: Lưu file vào két sắt
self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS)));
});

// 2. CHIẾN THUẬT: Stale-While-Revalidate (Lấy cái cũ trước, tải cái mới đè lên sau)
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      // Gọi fetch mới từ server để cập nhật
      const fetchPromise = fetch(event.request).then((networkResponse) => {
        // Nếu tải thành công, lưu đè vào cache
        if (networkResponse.status === 200) {
            caches.open(CACHE_NAME).then((cache) => cache.put(event.request, networkResponse.clone()));
        }
        return networkResponse;
      });

      // Trả về cái cũ ngay lập tức (để App mượt), sau đó cập nhật dữ liệu mới ở background
      return cachedResponse || fetchPromise;
    })
  );
});
