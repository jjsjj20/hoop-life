# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 50：桌面端界面宽度适配（v5.0.3）

【问题】用户反馈「功能适配新界面大小」——根因：#app 的 max-width:600px 是
  手机阅读限宽，v5.0.0 桌面布局重构后整个桌面界面（功能竖栏+事件区）都被压在
  600px 里，功能页/事件区显示拥挤。
【修法】桌面（≥900px）#app 放宽到 1080px；事件页/结果页（含 .scene 剧情内容）
  用 :has 精准限回 760px 居中阅读宽度（有剧情=限宽阅读），数据/功能页（无 .scene）
  通栏显示（表格/雷达/面板需要宽度）。纯 CSS 渐进增强（老浏览器事件页通栏可读）。
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


sub1(""".funcpage label{display:block;margin:14px 0 4px;color:var(--gold);font-size:12.5px;font-weight:700}""",
""".funcpage label{display:block;margin:14px 0 4px;color:var(--gold);font-size:12.5px;font-weight:700}
/* ── v5.0.3 桌面宽度适配：#app 放宽 + 事件页限阅读宽（:has 精准区分） ── */
@media(min-width:900px){
  #app{max-width:1080px}
  #stage:has(.scene){max-width:760px;margin:0 auto}   /* 事件/结果页限阅读宽；功能页（无 .scene）通栏 */
}""", '桌面宽度适配')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('桌面端界面宽度适配已应用：%d -> %d 字符（%+d）' % (orig, len(s), len(s) - orig))
