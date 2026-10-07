# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 35：球队实力模型调整（v4.24.0）

用户两条指示：
  ① 现役阵容取样：前 8 人平均值 → **前 10 人**平均值
  ② 阵容权重：55% → **70%**（俱乐部底子相应 45% → 30%）

背景（teamStrength 现状）：球队实力 = clamp(俱乐部底子×45% + 现役阵容×55%, 2~11)；
阵容 = 全队未退役球员按能力 o 排序取前 8 人平均，映射 clamp(6.4+(avg−74)×.75, 2, 10.5)。
调整后：底子只占三成，阵容成为主导项——「新星崛起改变联盟格局」的效应被放大，
球队底蕴（静态值）对战绩的权重被削弱；取样从 8 人扩到 10 人，把轮换深度也算进实力。

同步改动：
  · 阵容查看面板的「前 8 人均值」显示改为「前 10 人均值」（与 rosterStr 同口径）；
  · 三处注释里的 45%/8 人提法同步更新。
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


# ═══════════ 1. rosterStr：前 8 人 → 前 10 人 ═══════════
sub1("/* 阵容实力 → 球队星级（前 8 人平均能力映射回原来的 2~10 标尺） */",
     "/* 阵容实力 → 球队星级（前 10 人平均能力映射回原来的 2~10 标尺；v4.24.0 由前 8 人改为前 10 人） */",
     'rosterStr 注释')

sub1("  const top=rs.slice().sort((a,b)=>b.o-a.o).slice(0,8);",
     "  const top=rs.slice().sort((a,b)=>b.o-a.o).slice(0,10);",
     'rosterStr 取样人数')

# ═══════════ 2. teamStrength：55/45 → 70/30 ═══════════
sub1("""/* 球队实力 = 俱乐部底子(静态) + 当前阵容(会长会退)，让新星崛起真的改变联盟格局 */""",
     """/* 球队实力 = 俱乐部底子(静态 30%) + 当前阵容(70%，会长会退)，让新星崛起真的改变联盟格局
 * v4.24.0：阵容权重 55%→70%（底子 45%→30%）——阵容是球队实力的主导项 */""",
     'teamStrength 注释')

sub1("  return clamp((base||6)*.45+rs*.55,2,11);",
     "  return clamp((base||6)*.3+rs*.7,2,11);",
     'teamStrength 权重')

# ═══════════ 3. 阵容查看面板同口径 ═══════════
sub1("  const topN=rs.slice(0,8);",
     "  const topN=rs.slice(0,10);   /* v4.24.0：与 rosterStr 同口径（前 10 人） */",
     '阵容面板取样人数')

sub1("${avgTop?(' · 前 8 人均值 '+avgTop):''}",
     "${avgTop?(' · 前 10 人均值 '+avgTop):''}",
     '阵容面板文案')

# ═══════════ 4. 排名生成处注释 ═══════════
sub1("    /* 球队实力跟着阵容走：新星崛起 → 球队变强 → 排名上升（静态底子只占 45%） */",
     "    /* 球队实力跟着阵容走：新星崛起 → 球队变强 → 排名上升（静态底子只占 30%，v4.24.0：45%→30%） */",
     '排名注释')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('球队实力模型调整已应用：%d -> %d 字符（%+d）' % (orig, len(s), len(s) - orig))
