/**
 * AI虚拟文员 · Service Worker（PWA 离线缓存）
 * 策略：
 *   - /api/ 接口：直接走网络，绝不缓存（账目/税务数据必须最新）
 *   - 静态资源（/assets/、/icons/、manifest）：缓存优先，离线也能打开
 *   - 页面导航：网络失败时回退到缓存的首页（保证离线可打开）
 */
const CACHE_NAME = 'aiclerk-v1'
const CORE_ASSETS = ['/', '/manifest.webmanifest', '/icons/icon-192.png', '/icons/icon-512.png']

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches
      .open(CACHE_NAME)
      .then((cache) => cache.addAll(CORE_ASSETS))
      .then(() => self.skipWaiting())
  )
})

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  )
})

self.addEventListener('fetch', (event) => {
  const request = event.request
  if (request.method !== 'GET') return

  const url = new URL(request.url)
  if (url.origin !== self.location.origin) return

  // 接口请求永远走网络，保持数据最新
  if (url.pathname.startsWith('/api/')) return

  // 静态资源：缓存优先（构建产物带哈希，可安全缓存）
  if (url.pathname.startsWith('/assets/') || url.pathname.startsWith('/icons/')) {
    event.respondWith(
      caches.match(request).then((cached) => {
        if (cached) return cached
        return fetch(request).then((res) => {
          if (res.ok) {
            const clone = res.clone()
            caches.open(CACHE_NAME).then((cache) => cache.put(request, clone))
          }
          return res
        })
      })
    )
    return
  }

  // 页面导航：网络优先，失败回退缓存首页（离线可用）
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request).catch(() => caches.match('/').then((cached) => cached || caches.match('/index.html')))
    )
  }
})
