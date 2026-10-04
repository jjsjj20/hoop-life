# -*- coding: utf-8 -*-
"""给 sim_pacing.js 加 SIM_AGE（15 岁青训起步）支持。"""
import io

p = 'sim_pacing.js'
s = io.open(p, encoding='utf-8').read()

anchor = 'function runCareer(cfg) {'
assert anchor in s
s = s.replace(anchor, (
    "const AGE_INIT = Number(process.env.SIM_AGE || 18);   /* R2：SIM_AGE=15 青训起步 */\n"
    "const YOUTH = AGE_INIT < 18;\n\n"
    + anchor), 1)

old3 = ("    S.league=${JSON.stringify(cfg.league)}; S.mode=${JSON.stringify(cfg.mode)};\n"
        "    S.team=TEAMS[S.league==='NBA'?'nba':S.league==='CBA'?'cba':'euro'][0][0];\n"
        "    S.teamStr=6; S.age=18; S.stage='spring'; S.stageDone=0; S.stageNeed=stageNeedFor();")
new3 = ("    S.age=${AGE_INIT}; S.league=${JSON.stringify(YOUTH?'青训':cfg.league)}; "
        "S.mode=${JSON.stringify(cfg.mode)};\n"
        "    " + chr(36) + "{YOUTH ? \"S.team='山东高速青年队';S.teamStr=4;\" : "
        "\"S.team=TEAMS[S.league==='NBA'?'nba':S.league==='CBA'?'cba':'euro'][0][0];S.teamStr=6;\"}\n"
        "    S.stage='spring'; S.stageDone=0; S.stageNeed=stageNeedFor();")
assert old3 in s, 'bootstrap anchor not found'
s = s.replace(old3, new3)

# 删除旧的独立 league 行（已并入 new3）
old2 = ("      S.league=" + chr(36) + "{JSON.stringify(cfg.league)}; S.mode="
        + chr(36) + "{JSON.stringify(cfg.mode)};\n")
if old2 in s:
    s = s.replace(old2, '')

io.open(p, 'w', encoding='utf-8').write(s)
print('sim_pacing SIM_AGE done')
