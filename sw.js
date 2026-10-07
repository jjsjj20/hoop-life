/* 篮球人生 Service Worker（hoop-life-DEV）
 * HTML：网络优先（发版更新可达），断网回落缓存；
 * 其余同源资产：缓存优先（未命中拉取并入库）；
 * 跨域请求（AI 接口）一律不拦截；发版后旧缓存自动清理。 */
const CACHE = 'hoop-life-0d56778df6e9';
const CORE = ['./', './篮球人生.html', './manifest.json', './icons/icon-192.png', './icons/icon-512.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  let u;
  try { u = new URL(req.url); } catch (err) { return; }
  if (u.origin !== location.origin) return;   /* AI 接口等跨域请求不拦截 */
  if (req.mode === 'navigate') {              /* 页面：网络优先 */
    e.respondWith(
      fetch(req).then(r => {
        const cp = r.clone();
        caches.open(CACHE).then(c => c.put(req, cp));
        return r;
      }).catch(() => caches.match(req).then(m => m || caches.match('./篮球人生.html')))
    );
    return;
  }
  e.respondWith(                              /* 资产：缓存优先 */
    caches.match(req).then(m => m || fetch(req).then(r => {
      if (r.ok) {
        const cp = r.clone();
        caches.open(CACHE).then(c => c.put(req, cp));
      }
      return r;
    }))
  );
});
