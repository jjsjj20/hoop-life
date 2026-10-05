# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 30：整体移除 AI 点评层（v4.21.0）

评估结论（详见更新日志 v4.21.0）：
  · 代码侧并非不可修复——四轮补丁（v4.20.2~v4.20.5）修掉了空内容/回声/误报等全部已知代码问题；
  · 但残余失败（内容为空、复述要求、JSON 不合规）的根因在**外部模型与网络**，不在这份代码里，
    属于「重构无法消除」的可靠性上限；
  · 它是整个项目唯一的网络依赖与唯一的凭据依赖，而游戏本体（530 条手写事件）完全不需要它；
  · 该模块完全自包含（模块外零引用符号，仅 2 个入口按钮），删除是低风险外科手术；
  · 实现留在 git 历史（含本模块的最后一个提交），可随时恢复。

移除内容：
  ① 模块本体（`/* ═══ 12. AI 点评层（BYOK · 实验功能） ═══ */` 起，到自包装 IIFE 结束的 `})();`）；
  ② 行动栏的「🤖 AI」按钮；
  ③ ☰ 更多菜单里的「📰 新闻」入口。
"""
import os

BASE = os.path.dirname(os.path.abspath(__file__))
HTML = os.environ.get('GAME_HTML') or os.path.join(BASE, '..', 'output', '篮球人生.html')

s = open(HTML, encoding='utf-8').read()
orig = len(s)

START = '/* ═══════════ 12. AI 点评层（BYOK · 实验功能） ═══════════'
END = " try{window.renderGame=renderGame;}catch(e){}\n})();"

i0 = s.find(START)
if i0 < 0:
    raise SystemExit('!! 找不到 AI 模块起始标记')
i1 = s.find(END, i0)
if i1 < 0:
    raise SystemExit('!! 找不到 AI 模块结束标记')
i1 += len(END)
# 连带吃掉后面的空行，保持排版
while i1 < len(s) and s[i1] == '\n':
    i1 += 1
removed = i1 - i0
s = s[:i0] + s[i1:]

# ② 行动栏按钮
btn = '     <button onclick="AI.openPanel()">🤖 AI</button>\n'
n = s.count(btn)
if n != 1:
    raise SystemExit('!! AI 行动栏按钮匹配 %d 次' % n)
s = s.replace(btn, '')

# ③ ☰ 更多菜单入口
entry = "    mb('📰 新闻','AI.newsOpen()'),\n"
n = s.count(entry)
if n != 1:
    raise SystemExit('!! 更多菜单新闻入口匹配 %d 次' % n)
s = s.replace(entry, '')

# ④ 补回被连带删除的 SW 注册块
# v4.15 的 PWA 注册当初插在「AI.mount 之前」，而 AI.mount 属于被移除的模块——
# 这里把它放回模块外的稳定位置（图片预热之前），逻辑与 v4.15 原文一字不差。
SREG = """/* PWA（v4.15）：service worker 注册——仅在 http/https 下注册（file:// 直接打开不注册不报错） */
if('serviceWorker' in navigator&&/^https?:$/.test(location.protocol)){
  window.addEventListener('load',function(){navigator.serviceWorker.register('./sw.js').catch(function(){});});
}
"""
anchor = 'function warmArtImages(){'
if s.count(anchor) != 1:
    raise SystemExit('!! 找不到 warmArtImages 锚点')
s = s.replace(anchor, SREG + anchor)

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('AI 点评层已移除：删除 %d 字符 · 总字符 %d -> %d' % (removed, orig, len(s)))
