# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 15：P6 PWA 离线（v4.15.0）

  · manifest.json + service worker（sw.js）+ 应用图标（Pillow 从主视觉出 192/512 PNG）；
  · sw.js：HTML 网络优先（发版更新可达，断网回落缓存）、其余同源资产缓存优先
    （未命中拉取并入库）、旧版本缓存自动清理；跨域请求（AI API）一律不拦截；
  · 页面注册带协议守卫（file:// 直接打开不注册，不报错）；
  · AI 功能离线明示降级：断网时点击 AI 按钮给出「📴 暂不可用」提示，不影响存档与游戏。
"""
import os

BASE = os.path.dirname(os.path.abspath(__file__))
HTML = os.environ.get('GAME_HTML') or os.path.join(BASE, '..', 'output', '篮球人生.html')
OUT = os.path.dirname(HTML)

s = open(HTML, encoding='utf-8').read()
orig = len(s)


def sub1(old, new, why):
    global s
    n = s.count(old)
    if n != 1:
        raise SystemExit('!! %s 匹配 %d 次（期望 1）' % (why, n))
    s = s.replace(old, new)


VER = 'v4.15.0'

# ═══════════ 1. head：manifest + 主题色 + 触屏图标 ═══════════
sub1('<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">',
"""<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<link rel="manifest" href="./manifest.json">
<meta name="theme-color" content="#101830">
<link rel="apple-touch-icon" href="./icons/icon-192.png">""", 'head PWA 元信息')

# ═══════════ 2. SW 注册（协议守卫：file:// 不注册）═══════════
sub1("""AI.mount=function(){""",
"""/* PWA（v4.15）：service worker 注册——仅在 http/https 下注册（file:// 直接打开不注册不报错） */
if('serviceWorker' in navigator&&/^https?:$/.test(location.protocol)){
  window.addEventListener('load',function(){navigator.serviceWorker.register('./sw.js').catch(function(){});});
}
AI.mount=function(){""", 'SW 注册（协议守卫）')

# ═══════════ 3. AI 离线明示降级 ═══════════
sub1("""AI.go=function(el){
 if(AI.busy)return;""",
"""AI.go=function(el){
 if(AI.busy)return;
 if(typeof navigator!=='undefined'&&navigator.onLine===false){
  el.innerHTML='<div class="aiBox"><div class="aiNote">📴 当前离线：AI 功能暂不可用（不影响存档与游戏）</div></div>';
  return;
 }""", 'AI.go 离线明示降级')

# ═══════════ 4. manifest.json ═══════════
MANIFEST = """{
  "name": "篮球人生 · 生涯模拟",
  "short_name": "篮球人生",
  "description": "中文篮球生涯模拟文字游戏：从青训到退役，写你自己的篮球人生。",
  "lang": "zh-CN",
  "start_url": "./篮球人生.html",
  "scope": "./",
  "display": "standalone",
  "background_color": "#0a0f1f",
  "theme_color": "#101830",
  "icons": [
    { "src": "./icons/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "./icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any" }
  ]
}
"""
open(os.path.join(OUT, 'manifest.json'), 'w', encoding='utf-8', newline='\n').write(MANIFEST)
print('manifest.json 已生成')

# ═══════════ 5. service worker ═══════════
SW = """/* 篮球人生 Service Worker（""" + VER + """）
 * HTML：网络优先（发版更新可达），断网回落缓存；
 * 其余同源资产：缓存优先（未命中拉取并入库）；
 * 跨域请求（AI 接口）一律不拦截；发版后旧缓存自动清理。 */
const CACHE = 'hoop-life-""" + VER + """';
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
"""
open(os.path.join(OUT, 'sw.js'), 'w', encoding='utf-8', newline='\n').write(SW)
print('sw.js 已生成')

# ═══════════ 6. 应用图标（Pillow 从主视觉出 192/512 PNG）═══════════
try:
    from PIL import Image
    src = os.path.join(OUT, 'assets', 'art', 'hero.webp')
    im = Image.open(src).convert('RGB')
    w, h = im.size
    side = min(w, h)
    im = im.crop(((w - side) // 2, (h - side) // 2, (w + side) // 2, (h + side) // 2))
    ico_dir = os.path.join(OUT, 'icons')
    os.makedirs(ico_dir, exist_ok=True)
    im.resize((512, 512)).save(os.path.join(ico_dir, 'icon-512.png'), 'PNG')
    im.resize((192, 192)).save(os.path.join(ico_dir, 'icon-192.png'), 'PNG')
    print('图标已生成：icons/icon-192.png, icons/icon-512.png')
except Exception as e:
    print('图标生成跳过：', e)

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('PWA 已应用：%d -> %d 字符（%+d）' % (orig, len(s), len(s) - orig))
