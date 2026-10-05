# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 25：产出对齐（v4.20.1）

诊断：玩家与 NPC 共用 shootLine，但**期望分系数不同档**。以 OVR 92 为例：
  · 玩家：得分 o*.36-4 ≈ 29+（加成后 30~33）｜助攻 o*.10+(PG?o*.10) = 18.4（PG）
  · NPC 顶星（实测 npcSeasonLine，o=92 队内第 1）：21 分 / 6 板 / 10 助
→ 玩家在同能力下高出 40~84%，得分王/助攻王几乎必得、荣誉每季大满贯。

修复：把玩家三项系数对齐 NPC 产线（保留作者主角小幅优势 ~5%）：
  得分 .36 → .28（o=92：25.8-4=21.8 → 加队友/倾向加成后 ≈ 23，对 NPC 21）
  篮板 .08/.09 → .065/.07（o=92：6+6.4=12.4，对 NPC 内线 12）
  助攻 .10/.10/.03 → .06/.06/.02（o=92 PG：5.5+5.5=11，对 NPC PG 10）

防守数据两边同源（.55+能力/100*1.1 同式），不动。
球队总产出本来就守恒（calibrateNpc 从本队预算里扣玩家产量），不动。
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


sub1("""  const ppg0=clamp(Math.round((o*.36-4+tw.ppg+stabAdd()+tsAdd()+R.float(-4,4)*stabMul())*mul),2,capP);
  const rpg0=clamp(Math.round((o*.08+((pos==='C'||pos==='PF')?o*.09:0)+hustleRpgAdd()+R.float(-2,2))*mul),1,17);
  const apg0=clamp(Math.round((o*.10+(pos==='PG'?o*.10:pos==='SG'?o*.03:0)+tw.apg+tsNum()*ATTR.tsApg+R.float(-2,2))*mul),0,capA);""",
"""  /* v4.20.1 产出对齐：玩家三项系数对齐 NPC 产线（实测 o=92 顶星 21 分/6 板/10 助）——
   * 之前 .36/.10 档让同能力玩家高出 40~84%，得分王/助攻王几乎必得、荣誉每季大满贯。 */
  const ppg0=clamp(Math.round((o*.28-4+tw.ppg+stabAdd()+tsAdd()+R.float(-4,4)*stabMul())*mul),2,capP);
  const rpg0=clamp(Math.round((o*.065+((pos==='C'||pos==='PF')?o*.07:0)+hustleRpgAdd()+R.float(-2,2))*mul),1,17);
  const apg0=clamp(Math.round((o*.06+(pos==='PG'?o*.06:pos==='SG'?o*.02:0)+tw.apg+tsNum()*ATTR.tsApg+R.float(-2,2))*mul),0,capA);""", '玩家产出系数对齐')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('产出对齐已应用：%d -> %d 字符（%+d）' % (orig, len(s), len(s) - orig))
