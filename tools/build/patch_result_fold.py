# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 22：移动端结果页「剧情可折叠」（v4.19.2）

游玩反馈第四条：「结果也显示不全」。结果页会重放完整剧情文本（.scene）再跟
结果块（out / 数值变化 / 状态面板）——手机上结果信息被压在长文之下，得下滑才看得到。

方案（桌面完全不变）：
  · 结果页剧情块加 .sceneFold 类 + 一个「📖 展开剧情」开关（.foldBtn）；
  · 移动端默认收起剧情（.sceneFold:not(.show){display:none}）——结果直出；
    点开关即展开/收起（按钮文案同步切换）；
  · 桌面：.foldBtn 隐藏、剧情照常显示。
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


# ═══════════ 1. toggleSceneFold 函数（插在 renderTop 前，与 HUD_MIN 相邻）═══════════
sub1("""/* 移动端 HUD 收起（v4.19.0）：顶部信息占屏太多时，一键收起只留人名行，localStorage 记忆 */""",
"""/* 移动端结果页剧情折叠（v4.19.2）：默认收起剧情让结果直出，点开关展开回顾 */
function toggleSceneFold(){
  const sc=document.getElementById('resScene'),bt=document.getElementById('resFoldBtn');
  if(!sc||!bt)return;
  const show=sc.classList.toggle('show');
  bt.textContent=show?'📖 收起剧情':'📖 展开剧情';
}
/* 移动端 HUD 收起（v4.19.0）：顶部信息占屏太多时，一键收起只留人名行，localStorage 记忆 */""", 'toggleSceneFold 函数')

# ═══════════ 2. 结果页剧情块加类 + 开关按钮（用 .result 上下文唯一锚）═══════════
sub1("""<div class="scene">${paras(ev.scene)}</div>
  <div class="result">""",
"""<div class="scene sceneFold" id="resScene">${paras(ev.scene)}</div>
  <button class="btn ghost small foldBtn" id="resFoldBtn" onclick="toggleSceneFold()">📖 展开剧情</button>
  <div class="result">""", '结果页剧情块与开关')

# ═══════════ 3. CSS：桌面隐藏开关；移动端默认收起剧情 ═══════════
sub1(""".contAct{display:none}""",
""".contAct{display:none}
.foldBtn{display:none}""", 'foldBtn 桌面隐藏')
sub1("""  .contAct{display:block;background:linear-gradient(180deg,#f97316,#ea580c);border-color:#fb923c;color:#fff;font-weight:800}
}""",
"""  .contAct{display:block;background:linear-gradient(180deg,#f97316,#ea580c);border-color:#fb923c;color:#fff;font-weight:800}
  .foldBtn{display:block;width:100%;margin:0 0 10px}
  .sceneFold:not(.show){display:none}
}""", '移动端折叠样式')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('结果页剧情折叠已应用：%d -> %d 字符（%+d）' % (orig, len(s), len(s) - orig))
