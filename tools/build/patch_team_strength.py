# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 35：球队实力模型调整（v4.24.0 → v4.25.0）

【v4.24.0】用户两条指示：
  ① 现役阵容取样：前 8 人平均值 → 前 10 人平均值
  ② 阵容权重：55% → 70%（俱乐部底子相应 45% → 30%）

【v4.25.0】继续放大阵容权重（同日第二轮指示）：
  ① 取样：前 10 人 → **前 13 人**
  ② 权重：70% → **80%**（俱乐部底子 30% → 20%）

  取样深度补偿（本轮新增）：名单规格 fixed——NBA 全队 14~15 人 / CBA 8~12 /
  欧洲 6~10 / NCAA 5~8（见 fixRosterAll）。前 13 人取样**只截断 NBA**，
  且截断会压低均值：25 队实测不补偿时 NBA 联盟标尺整体下移 1.53 分
  （等效季后赛对手集体变弱、吃掉 v4.22/v4.23 刚校准的难度）。
  因此对「名单 >13 人」的联赛补 2.2 映射分（校准探针：−1.53 → −0.03）；
  CBA/欧洲/NCAA 取样即全队、无深度效应，不补偿（实测变化 +0.05/−0.25/−0.01）。

最终形态：球队实力 = clamp(底子×20% + (前13人均值映射 + 深度补偿)×80%, 2~11)。

同步改动：阵容查看面板「前 13 人均值」同口径；三处注释的权重/人数提法更新。
边界：S.teamStr（球员视角的底子快照）与球员亲打的单场模拟不受影响；
degraded 路径（阵容 <5 人时退回纯底子）不变。
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


# ═══════════ 1. rosterStr：前 8 人 → 前 13 人 + 取样深度补偿 ═══════════
sub1("/* 阵容实力 → 球队星级（前 8 人平均能力映射回原来的 2~10 标尺） */",
     "/* 阵容实力 → 球队星级（前 13 人平均能力映射回原来的 2~10 标尺；v4.25.0：前 8→13 人 + 深度补偿） */",
     'rosterStr 注释')

sub1("""  const top=rs.slice().sort((a,b)=>b.o-a.o).slice(0,8);
  const avg=top.reduce((s,p)=>s+p.o,0)/top.length;
  return clamp(6.4+(avg-74)*.75,2,10.5);""",
     """  const top=rs.slice().sort((a,b)=>b.o-a.o).slice(0,13);
  const avg=top.reduce((s,p)=>s+p.o,0)/top.length;
  /* v4.25.0 取样深度补偿：名单规格 NBA 14~15 / CBA 8~12 / 欧洲 6~10 / NCAA 5~8，
   * 前 13 人取样只截断 NBA——截断会把均值压低（实测全联盟下移 1.53 分）。
   * 对 >13 人的联赛补 2.2 映射分把标定拉回旧版；其余联赛取样即全队，不补偿。 */
  const deep=rs.length>13?2.2:0;
  return clamp(6.4+(avg-74)*.75+deep,2,10.5);""",
     'rosterStr 取样与补偿')

# ═══════════ 2. teamStrength：55/45 → 80/20 ═══════════
sub1("""/* 球队实力 = 俱乐部底子(静态) + 当前阵容(会长会退)，让新星崛起真的改变联盟格局 */""",
     """/* 球队实力 = 俱乐部底子(静态 20%) + 当前阵容(80%，会长会退)，让新星崛起真的改变联盟格局
 * v4.25.0：阵容权重 70%→80%（底子 30%→20%）——阵容是球队实力的绝对主导项 */""",
     'teamStrength 注释')

sub1("  return clamp((base||6)*.45+rs*.55,2,11);",
     "  return clamp((base||6)*.2+rs*.8,2,11);",
     'teamStrength 权重')

# ═══════════ 3. 阵容查看面板同口径 ═══════════
sub1("  const topN=rs.slice(0,8);",
     "  const topN=rs.slice(0,13);   /* v4.25.0：与 rosterStr 同口径（前 13 人） */",
     '阵容面板取样人数')

sub1("${avgTop?(' · 前 8 人均值 '+avgTop):''}",
     "${avgTop?(' · 前 13 人均值 '+avgTop):''}",
     '阵容面板文案')

# ═══════════ 4. 排名生成处注释 ═══════════
sub1("    /* 球队实力跟着阵容走：新星崛起 → 球队变强 → 排名上升（静态底子只占 45%） */",
     "    /* 球队实力跟着阵容走：新星崛起 → 球队变强 → 排名上升（静态底子只占 20%，v4.25.0：45%→20%） */",
     '排名注释')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('球队实力模型调整已应用：%d -> %d 字符（%+d）' % (orig, len(s), len(s) - orig))
