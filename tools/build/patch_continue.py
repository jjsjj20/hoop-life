# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 21：移动端「继续」吸底（v4.19.1）

游玩反馈第三条：「手机上选完后还要下滑点继续」。结果页的「继续 ▶」按钮
落在 #stage 内容流末尾——选项结算信息一多，就得下滑才够得着。

方案（桌面完全不变）：
  · 结果页原按钮加 .contBtn 类；
  · 行动栏（v4.19.0 已吸底）在结果模式下多渲染一个高亮「继续 ▶」(.contAct)；
  · 移动端：隐藏原按钮、行动栏继续按钮显示为橙色主行动；
  · 桌面：.contAct 默认 display:none——一切照旧。
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


# ═══════════ 1. 结果页原按钮加类 ═══════════
sub1("""  <button class="btn" onclick="advance()">继续 ▶</button>`;""",
"""  <button class="btn contBtn" onclick="advance()">继续 ▶</button>`;""", '结果页按钮加类')

# ═══════════ 2. 行动栏：结果模式多渲染一个吸底「继续」═══════════
sub1("""     <button onclick="showRoster()">👥 阵容</button>""",
"""     ${UI.mode==='result'?'<button class="contAct" onclick="advance()">继续 ▶</button>':''}
     <button onclick="showRoster()">👥 阵容</button>""", '行动栏继续按钮')

# ═══════════ 3. CSS：桌面隐藏 .contAct；移动端隐藏原按钮、显示吸底继续 ═══════════
sub1(""".hudmin{display:none;align-items:center;justify-content:center;""",
""".contAct{display:none}
.hudmin{display:none;align-items:center;justify-content:center;""", 'contAct 桌面隐藏')
sub1("""  .actions button{min-width:0;height:42px;font-size:13px;padding:0 6px}
}""",
"""  .actions button{min-width:0;height:42px;font-size:13px;padding:0 6px}
  .contBtn{display:none}
  .contAct{display:block;background:linear-gradient(180deg,#f97316,#ea580c);border-color:#fb923c;color:#fff;font-weight:800}
}""", '移动端继续按钮样式')

# ═══════════ 4. renderResult 末尾：把「继续」注入吸底行动栏 ═══════════
# （choose() 结算后直接调 renderResult、不重渲整页——行动栏需就地注入）
sub1("""  <button class="btn contBtn" onclick="advance()">继续 ▶</button>`;
  kbHint();
}""",
"""  <button class="btn contBtn" onclick="advance()">继续 ▶</button>`;
  /* v4.19.1：把「继续」同步放进吸底行动栏（桌面由 CSS 隐藏，移动端显示为橙色主行动） */
  try{
    const _act=document.querySelector('.actions');
    if(_act&&!_act.querySelector('.contAct'))
      _act.insertAdjacentHTML('afterbegin','<button class="contAct" onclick="advance()">继续 ▶</button>');
  }catch(e){}
  kbHint();
}""", 'renderResult 注入吸底继续')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('继续按钮吸底已应用：%d -> %d 字符（%+d）' % (orig, len(s), len(s) - orig))
