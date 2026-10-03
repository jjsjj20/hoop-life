# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 4：首屏图片的加载时序优化。

拆成外链之后有个新问题：首屏主视觉 hero 是 renderMenu() 在脚本跑完才拼出来的，
浏览器要等 700KB 的 HTML 解析完 + 脚本执行完，才开始下载它——白白多等一个来回。
另外 68 张队徽是纯装饰，不该跟主图抢带宽。

这里做三件事：
  1. <head> 里 preload 首屏主视觉，让它在解析 HTML 的同时就并行下载；
  2. 给主视觉加 fetchpriority="high"，给装饰性的队徽/成就图标加 fetchpriority="low"；
  3. 空闲时按低优先级预热 19 张场景插画（省流/慢网跳过），让之后每次翻页都不用等图。
"""
import os, re

BASE = os.path.dirname(os.path.abspath(__file__))
HTML = os.environ.get('GAME_HTML') or os.path.join(BASE, '..', 'output', '篮球人生.html')

s = open(HTML, encoding='utf-8').read()
orig = len(s)


def sub1(old, new, why):
    n = s.count(old)
    if n != 1:
        raise SystemExit('!! %s 匹配 %d 次' % (why, n))
    return s.replace(old, new)


# ═══════════ 1. head 里 preload 首屏主视觉 ═══════════
s = sub1(
    '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">',
    '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">\n'
    '<!-- 首屏主视觉提前发起下载：它原本要等脚本跑完 renderMenu() 才被发现，白白慢一个来回 -->\n'
    '<link rel="preload" as="image" href="assets/art/hero.webp" fetchpriority="high">',
    'preload 首屏主视觉')

# ═══════════ 2. 优先级提示 ═══════════
# 主视觉：首屏第一眼，给高优先级
s = sub1(
    '<img src="assets/art/hero.webp" alt="" decoding="async">',
    '<img src="assets/art/hero.webp" alt="" decoding="async" fetchpriority="high">',
    'hero 提优先级')
# 队徽 / 成就图标：装饰性，压到低优先级别抢带宽
s = sub1(
    """'<img class="tcrest" src="'+c+'" alt="" loading="lazy" decoding="async">'""",
    """'<img class="tcrest" src="'+c+'" alt="" loading="lazy" decoding="async" fetchpriority="low">'""",
    'tcrest 降优先级')
s = sub1(
    """'<img src="'+crestData(t)+'" alt="" loading="lazy" decoding="async">'""",
    """'<img src="'+crestData(t)+'" alt="" loading="lazy" decoding="async" fetchpriority="low">'""",
    '成就页队徽降优先级')
s = sub1(
    """<img src="${_ic}" alt="" loading="lazy" decoding="async">""",
    """<img src="${_ic}" alt="" loading="lazy" decoding="async" fetchpriority="low">""",
    '成就图标降优先级')

# ═══════════ 3. 空闲预热场景插画 ═══════════
WARM = r"""
/* ═══════════ 11.6 场景插画预热 ═══════════
 * 事件插图是按「本页氛围」现挑的（artMood → ART_IMG），所以只有翻开那一页才开始下载，
 * 每次都要干等一个来回。这里在空闲时按低优先级把 19 张拉进浏览器缓存，
 * 之后翻页基本就是秒出。省流模式 / 2G / 3G 下直接跳过，不替玩家花流量。
 */
function warmArtImages(){
  try{
    var c=navigator.connection||navigator.mozConnection||navigator.webkitConnection;
    if(c&&(c.saveData||/(^|-)2g$|(^|-)3g$/.test(String(c.effectiveType||''))))return;
    var keys=Object.keys(ART_IMG),i=0,seen={};
    (function next(){
      var url=null;
      while(i<keys.length){                       /* ART_IMG.court 是 arena 的别名，去重 */
        var u=ART_IMG[keys[i++]];
        if(u&&!seen[u]){seen[u]=1;url=u;break;}
      }
      if(!url)return;
      var im=new Image();
      try{im.fetchPriority='low';}catch(_){}
      im.onload=im.onerror=function(){setTimeout(next,220);};  /* 串行 + 间隔，别挤占交互请求 */
      im.src=url;
    })();
  }catch(_){}
}
setTimeout(function(){
  if(window.requestIdleCallback)requestIdleCallback(warmArtImages,{timeout:4000});
  else warmArtImages();
},2500);
"""
s = sub1(
    "renderMenu();\n",
    "renderMenu();\n" + WARM,
    '插入插画预热')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('加载时序优化完成：%d -> %d 字符' % (orig, len(s)))
