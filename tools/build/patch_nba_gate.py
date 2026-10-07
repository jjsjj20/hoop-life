# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 34：NBA 门槛（选秀后移 + FMVP 修正）（v4.23.0）

游玩反馈两条一起来的：「还是太简单了，一名 68 左右评分的球员不仅能拿总冠军
还能拿 mvp」+「提升进入 nba 的难度」。

【一】选秀行情整体后移（draftStockInit）
  七轮 jsdom 探针实测（含试训加成 +2~6/+1~4 与球队承诺救援，age 20 · 500 次）：
    现役：70 分即 0% 落选（「练到 70 就保送 NBA」）；64~66 分 65% 落选；
          75~77 分首轮率 36~40%。
    新档：每个评分段的行情普遍差 4~12 位——
          70~73 分落选 13~16% · 68 分落选 17%→51% · 64~66 分 65%→89~93%；
          75~77 分首轮率 36~40%→15%（顺位预期从中段滑到次轮）。
  落选不是终点：10 天短合同 / 发展联盟 / CBA 通道照旧，19~23 岁每年还能再申报。

【二】FMVP 概率改为随实力起跳
  旧 NBA 公式 clamp(.35+(o−78)*.05,.35,.85) 下限锁死 35%——68 分球员随强队夺冠
  （实测 59.1%）后 35% 概率拿 FMVP，每赛季约 20%，「角色球员总决赛 MVP」成为
  高频事件（用户「68 分能拿 mvp」的直接来源；常规赛 MVP 榜实测 68 分只排 46 名，
  本就够不着前三）。新公式基线 .05+(o−70)*.05：o70 → 5%，o78 → 45%，o82 → 65%，
  o86+ → 85%；常规赛 MVP 榜前三再 +20%。
  旧 CBA/欧洲公式固定 .45（榜单前 6 即触发）同改：基线同款 + 榜单前三再 +15%——
  o78 榜外仍 45%（与原值持平），o73 → 20%，o68 → 5%。
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


# ═══════════ 1. 选秀行情整体后移 ═══════════
sub1("""  if(o>=86)base=R.float(3,9);
  else if(o>=82)base=R.float(7,16);
  else if(o>=78)base=R.float(13,24);
  else if(o>=74)base=R.float(20,33);
  else if(o>=70)base=R.float(28,44);
  else if(o>=67)base=R.float(38,54);
  else if(o>=64)base=R.float(48,62);
  else base=R.float(56,72);""",
"""  /* v4.23.0 选秀门槛整体后移：同评分段的行情普遍差 4~12 位——NBA 不再是
   * 「练到 70 分就保送」。真实链路实测（含试训加成与承诺救援，age 20 · 500 次）：
   * 70~73 分 落选 0%→13~16% · 68 分 17%→51% · 64~66 分 65%→89~93%；
   * 75~77 分 首轮率 36~40%→15%（顺位预期从中段滑到次轮）。 */
  if(o>=86)base=R.float(4,12);
  else if(o>=82)base=R.float(9,20);
  else if(o>=78)base=R.float(15,28);
  else if(o>=74)base=R.float(24,42);
  else if(o>=70)base=R.float(33,55);
  else if(o>=67)base=R.float(43,62);
  else if(o>=64)base=R.float(53,70);
  else base=R.float(61,76);""", '选秀行情档位')

# ═══════════ 2. NBA FMVP：去掉 35% 下限 ═══════════
sub1("""    if(R.chance(clamp(.35+(o-78)*.05+(top?.2:0),.35,.85)))H.push('NBA总决赛MVP（FMVP）');""",
"""    /* v4.23.0：FMVP 概率改为随实力起跳——旧公式下限锁死 35%，68 分球员夺冠后
     * 也有 35% 拿 FMVP（59.1% 夺冠率 × 35% ≈ 每季 20%），「角色球员总决赛 MVP」
     * 成为高频事件。新公式：o70 → 5%，o78 → 45%，o82 → 65%，o86+ → 85%。 */
    if(R.chance(clamp(.05+(o-70)*.05+(top?.2:0),.05,.85)))H.push('NBA总决赛MVP（FMVP）');""", 'NBA FMVP 公式')

# ═══════════ 3. CBA/欧洲 FMVP：同款随实力起跳 ═══════════
sub1("""      if(cfg.fmvp&&_board&&_board.my&&_board.my.mvp<=6&&R.chance(.45))H.push(cfg.fmvp);""",
"""      /* v4.23.0：同 NBA——固定 45% 改为随实力起跳（常规赛 MVP 榜前三另 +15%）：
       * o70 → 5%，o73 → 20%，o78 榜外 → 45%（与原值持平），o78 榜三 → 60%。 */
      if(cfg.fmvp&&_board&&_board.my&&_board.my.mvp<=6&&R.chance(clamp(.05+(o-70)*.05+(_board.my.mvp<=3?.15:0),.05,.85)))H.push(cfg.fmvp);""", 'CBA/欧洲 FMVP 公式')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('NBA 门槛（选秀后移 + FMVP 修正）已应用：%d -> %d 字符（%+d）' % (orig, len(s), len(s) - orig))
