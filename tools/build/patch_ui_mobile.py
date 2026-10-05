# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 20：移动端布局优化（v4.19.0）

游玩反馈第二条：「手机游玩要上下滑动因为看不全」。根因：移动端竖向堆叠里
「外壳」占掉太多——顶部 HUD 常驻（sticky，含四季阶段条 + 7 个 chips 换行）、
章节行、128px 插画，加 20px 下距的行动栏落在首屏之外。

方案（桌面完全不变，仅 @media(max-width:899px)）：
  ① HUD 可收起：右上角 ▴/▾ 一键收起阶段条与 chips（只留人名行），localStorage 记忆；
  ② 行动栏吸底：sticky bottom——5 个按钮（阵容/排名/AI/存档/☰ 更多）随时可见，
     不必滑到底；并压扁为一排（min-width:0 / 42px 高）；
  ③ 插画 128→96px、章节行/事件标题/场景与选项间距同步压缩，一屏多装约 150px 内容。
"""
import os

BASE = os.path.dirname(os.path.abspath(__file__))
HTML = os.environ.get('GAME_HTML') or os.path.join(BASE, '..', 'output', '篮球人生.html')

s = open(HTML, encoding='utf-8').read()
orig = len(s)


def sub1(old, new, why):
    global s
    n = s.count(old)
    if n != 1:
        raise SystemExit('!! %s 匹配 %d 次（期望 1）' % (why, n))
    s = s.replace(old, new)


# ═══════════ 1. CSS：移动端布局块 + .hudmin 基础态 ═══════════
sub1("""@media(max-width:430px){.heroArt{height:200px}.heroTx{padding:18px 10px 50px}.hero h1{font-size:26px}.art{height:112px}.art .artsym{font-size:62px}.art .artcap{right:96px;font-size:11.5px}}""",
"""@media(max-width:430px){.heroArt{height:200px}.heroTx{padding:18px 10px 50px}.hero h1{font-size:26px}.art{height:112px}.art .artsym{font-size:62px}.art .artcap{right:96px;font-size:11.5px}}
/* 移动端布局优化（v4.19.0）：HUD 可收起 + 行动栏吸底 + 插画/间距压缩——一屏看得更多 */
.hudmin{display:none;align-items:center;justify-content:center;width:28px;height:28px;flex:0 0 auto;
  border-radius:9px;border:1px solid #273046;background:var(--btn2);color:var(--muted);font-size:12px;cursor:pointer}
.hudmin:hover{border-color:#3d4a66;color:var(--txt)}
@media(max-width:899px){
  .hud{padding:6px 12px 7px}
  .hud.min .stagebar,.hud.min .chips{display:none}
  .hudmin{display:flex}
  .chapter{margin:8px 0 4px;font-size:11.5px;letter-spacing:1.2px}
  .etitle{font-size:19px;margin:2px 0 9px}
  .art{height:96px;margin:0 0 10px}
  .scene{padding:12px 14px 12px 18px;font-size:14.5px}
  .scene p{margin:0 0 9px}
  #stage{min-height:180px}
  .actions{position:sticky;bottom:0;z-index:7;margin-top:12px;padding:8px 0 calc(8px + env(safe-area-inset-bottom));
    background:linear-gradient(180deg,rgba(8,10,17,0),rgba(8,10,17,.94) 30%,rgba(8,10,17,.98))}
  .actions button{min-width:0;height:42px;font-size:13px;padding:0 6px}
}""", '移动端 CSS 块')

# ═══════════ 2. HUD_MIN 状态 + 切换函数（renderTop 之前）═══════════
sub1("""function renderTop(){""",
"""/* 移动端 HUD 收起（v4.19.0）：顶部信息占屏太多时，一键收起只留人名行，localStorage 记忆 */
const HUDMIN_KEY='hl_hudmin';
let HUD_MIN=(function(){try{return localStorage.getItem(HUDMIN_KEY)==='1';}catch(e){return false;}})();
function toggleHudMin(){
  HUD_MIN=!HUD_MIN;
  try{localStorage.setItem(HUDMIN_KEY,HUD_MIN?'1':'0');}catch(e){}
  renderGame();
}
function renderTop(){""", 'HUD_MIN 与切换函数')

# ═══════════ 3. renderTop：hud 类名 + 收起按钮 ═══════════
sub1("""  return `<div class="hud">
  <div class="hudrow">${ringHTML(who.v,'OVR')}
   <div class="who"><b>${esc(who.n)}</b><span>${who.s}</span></div>
   <span class="chip">${who.tag}</span>""",
"""  return `<div class="hud${HUD_MIN?' min':''}">
  <div class="hudrow">${ringHTML(who.v,'OVR')}
   <div class="who"><b>${esc(who.n)}</b><span>${who.s}</span></div>
   <span class="chip">${who.tag}</span><button class="hudmin" onclick="toggleHudMin()" title="收起/展开顶部信息">${HUD_MIN?'▾':'▴'}</button>""", 'hud 类名与收起按钮')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('移动端布局优化已应用：%d -> %d 字符（%+d）' % (orig, len(s), len(s) - orig))
