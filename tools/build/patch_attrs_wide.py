# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 45：桌面通栏收窄——只有属性页适配新界面大小（v5.0.4）

【问题】用户反馈「只有属性适配新界面大小」——v5.0.3 把所有功能页（无 .scene）
  全部放开通栏（~950px），范围过大。实际只有「📊 属性」页（showAttrs，竖条
  色条列表）需要大宽度，其他功能页应保持限宽阅读。
【修法】#stage 桌面默认限回 760px 居中；属性页内容包 .attrswide 标记类，
  :has 放开通栏。事件页（.scene）随 #stage 默认值，原 :has(.scene) 规则删除。
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


# 1) CSS：#stage 默认限宽，仅属性页通栏
sub1("""  #app{max-width:1080px}
  #stage:has(.scene){max-width:760px;margin:0 auto}   /* 事件/结果页限阅读宽；功能页（无 .scene）通栏 */
}""",
"""  #app{max-width:1080px}
  #stage{max-width:760px;margin:0 auto}               /* 事件/功能页默认限阅读宽 */
  #stage:has(.attrswide){max-width:none}              /* 仅属性页通栏（v5.0.4 收窄） */
}""", '桌面通栏收窄')

# 2) showAttrs：内容包 .attrswide 标记（openOvl 桌面分支原样放入 #stage）
sub1("""  openOvl('<h3>📊 '+esc(S.name)+' · OVR <b style="color:#fbbf24">'+ovr()+'</b></h3>'""",
"""  openOvl('<div class="attrswide"><h3>📊 '+esc(S.name)+' · OVR <b style="color:#fbbf24">'+ovr()+'</b></h3>'""",
      '属性页开标签')

sub1("""    +grp('⚡ 身体素质',[['速度',k.speed||55],['力量',k.strength||55],['身体基础',ab]])
    +'<button class="btn ghost" style="margin-top:14px" onclick="closeOvl()">关闭</button>');""",
"""    +grp('⚡ 身体素质',[['速度',k.speed||55],['力量',k.strength||55],['身体基础',ab]])
    +'<button class="btn ghost" style="margin-top:14px" onclick="closeOvl()">关闭</button></div>');""",
      '属性页闭标签')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('桌面通栏收窄（仅属性页）已应用：%d -> %d 字符（%+d）' % (orig, len(s), len(s) - orig))
