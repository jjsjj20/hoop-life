# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 44：季后赛断/帽场均显示精度修复（v4.29.1）

【问题】用户截图反馈：季后赛面板「场均 × 场次 ≠ 总计」——
  场均 1.1断 × 5场 = 5.5，但总计显示 5.3；0.4帽 × 5 = 2.0，总计 2.1。
【根因】数据本身自洽（总计 5.3 ÷ 5 = 1.06），但断/帽场均只显示 1 位小数——
  短系列赛（5~7 场）里断/帽数量级小（0.4~1.5），1 位小数的量化误差
  （±0.05×场次 = ±0.25~0.35）被放大成「肉眼可见的对不上」。
【修法】断/帽场均改为 2 位小数（1.06 / 0.42）——×场次后与总计严格一致；
  得分/篮板/助攻保持原精度（数量级大，1 位小数自洽且更 2K）。
  数据源头（po.stl/po.blk 原始累计）不动，纯显示精度修复。
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


sub1("""      spg:Math.round((po.stl||0)/po.games*10)/10,bpg:Math.round((po.blk||0)/po.games*10)/10,""",
"""      spg:Math.round((po.stl||0)/po.games*100)/100,bpg:Math.round((po.blk||0)/po.games*100)/100,   /* v4.29.1：断/帽场均 2 位小数——1 位时场均×场次与总计对不上（观感 bug） */""", '断/帽场均 2 位')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('季后赛断/帽场均精度修复已应用：%d -> %d 字符（%+d）' % (orig, len(s), len(s) - orig))
