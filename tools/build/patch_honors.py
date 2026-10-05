# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 24：荣誉与冠军校准（v4.20.0 第二批）

诊断证据（单生涯逐季 dump，高天赋档）：
  新秀季（20 岁）一次拿到 12 项荣誉：助攻王+MVP+一阵+一防+全明星+最佳新秀+
  最佳第六人+最佳关键球员+总冠军+FMVP+进步最快+新秀一阵——此后每季固定 6~10 项，
  42 岁 154 项。也就是说：玩家一旦能力堆起来，联盟里没有任何东西能拦住他。

两处校准（不做产出公式大改，只把「拦不住」的地方收紧）：
  ① 玩家对球队胜率的加成 adj*.005 → .003：顶星不再凭一己之力把球队抬到稳冠；
  ② 荣誉门槛收紧：
     · MVP/DOPY 概率下调（.55/.28/.10 → .42/.16/.05；防守 .45/.22/.08 → .36/.15/.05）
     · 最佳第六人：新秀不给（避免「新秀冠军+MVP+第六人」同框）
     · 最佳关键球员：联盟前 4（原前 6）且大心脏 ≥88（原 82）
     · 进步最快：至少打到第 2 个赛季（原第 1 季就能拿）、排名 ≤10（原 ≤14）、概率 .35→.25
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


# ═══════════ ① 玩家对球队胜率的加成下调 ═══════════
sub1("      wpc=clamp(.38-lgHard(lg).wpc+(st-6.5)*.055+adj*.005-tankPad+R.float(-.06,.06),.06,.95);",
     "      wpc=clamp(.38-lgHard(lg).wpc+(st-6.5)*.055+adj*.003-tankPad+R.float(-.06,.06),.06,.95);   /* v4.20.0：顶星对球队胜率的加成 .005→.003——冠军不再是一人之力 */",
     '球队加成下调')

# ═══════════ ② MVP / DPOY 概率下调 ═══════════
sub1("""  const base=[.55,.28,.10];
  if(cfg.mvp&&rank('mvp')<=3&&R.chance(base[rank('mvp')-1]+(res&&res.champ?.12:0)))H.push(cfg.mvp);
  if(cfg.dpoy&&rank('def')<=3&&R.chance([.45,.22,.08][rank('def')-1]))H.push(cfg.dpoy);""",
"""  /* v4.20.0：MVP/DPOY 概率下调——前三名也不再是「常客价」 */
  const base=[.42,.16,.05];
  if(cfg.mvp&&rank('mvp')<=3&&R.chance(base[rank('mvp')-1]+(res&&res.champ?.10:0)))H.push(cfg.mvp);
  if(cfg.dpoy&&rank('def')<=3&&R.chance([.36,.15,.05][rank('def')-1]))H.push(cfg.dpoy);""", 'MVP 概率')

# ═══════════ ③ 第六人：新秀不给 ═══════════
sub1("""  if(cfg.six&&!S.starter&&rank('mvp')<=8)H.push(cfg.six);
  if(cfg.clutch&&rank('mvp')<=6&&(S.skills.clutch||60)>=82)H.push(cfg.clutch);""",
"""  /* v4.20.0：第六人非新秀才给；最佳关键球员门槛提高（前 4 + 大心脏 ≥88） */
  if(cfg.six&&!S.starter&&!rookie&&rank('mvp')<=8)H.push(cfg.six);
  if(cfg.clutch&&rank('mvp')<=4&&(S.skills.clutch||60)>=88)H.push(cfg.clutch);""", '第六人/关键球员')

# ═══════════ ④ 进步最快：更严格的进步门槛 ═══════════
sub1("""    if(cfg.mip&&!S.flags.gotMIP&&(S.career.seasons||0)>=1&&o>=70&&_board&&_board.my&&_board.my.mvp<=14&&R.chance(.35)){""",
"""    /* v4.20.0：进步最快至少第 2 季、排名 ≤10、概率 .25——不再「新秀季即进步最快」 */
    if(cfg.mip&&!S.flags.gotMIP&&(S.career.seasons||0)>=2&&o>=70&&_board&&_board.my&&_board.my.mvp<=10&&R.chance(.25)){""", '进步最快门槛')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('荣誉与冠军校准已应用：%d -> %d 字符（%+d）' % (orig, len(s), len(s) - orig))
