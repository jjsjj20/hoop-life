# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 33：季后赛对抗烈度——对手拔高（v4.22.0）

游玩反馈：「让球队夺冠的难度增加」。五轮 jsdom 探针实测（500 次完整对阵图）：
  NBA 2 号种子球星档（teamStr 7 · OVR 76）基线夺冠率 78.4%——摆烂档实测
  「两季摆烂两连冠」同源：球星带队（个人表现 swing 修正）+ 强队底子，
  季后赛对手照纸面实力打，系列赛形同走过场。

已证伪的候选杠杆：
  · LG_HARD.po（每场我方减压）：.28→.85 夺冠率仅 90%→84.7%——Math.max(58) 下限
    与个人 swing 修正把分差效应吞掉，弱旋钮；
  · 按「我队纸面实力 − 对手实力」递进加成：季后赛对手全是强队（str 6.5-8.5），
    差值只有 0.5-1.5，bump 被压到 0.6 以下，几乎无效（94.5%→92.5%）。

最终方案：季后赛系列赛的每个对手都拔高一档（对抗烈度）——
  NBA +1.5、CBA +2.5（对手普遍偏弱、轮次少一轮，需要更大修正）、欧洲 +1.0。
定案实测（500 次/原型，与 patch 实现逐字一致）：
  NBA 顶级（1号种子 teamStr8）96.2%→87.0%（历史级球队仍该被看好）
  NBA 球星（2号种子 teamStr7）78.4%→48.4%（强队夺魁变成真五五开）
  NBA 中档（6号种子 teamStr5.5）21.0%→4.8%（下限种子回归现实）
  CBA 球星（2号种子 teamStr7）96.2%→69.2%
  附带：系列赛平均长度 4.7→5.6 场（天王山/抢七显著变多）。
边界：附加赛走掷骰判定不经此函数；NPC 之间对阵（simWinnerOf）不受影响，
联盟生态与新闻叙事不变——只有玩家打的部分变难。
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


# ═══════════ seriesOppStr：对手拔高 ═══════════
sub1("""function seriesOppStr(game){
  const o=seriesOpponentOf();
  return o&&o.str?o.str:6;
}""",
"""/* v4.22.0 季后赛对抗烈度：系列赛每个对手都打出超出纸面实力的一档篮球
 * （全民皆兵 + 谁都想掀翻强队）。NBA +1.5、CBA +2.5（对手偏弱且少一轮，
 * 需要更大修正）、欧洲 +1.0。500 次完整对阵图实测见 patch 头注：
 * NBA 2号种子夺冠率 78.4%→48.4%、CBA 96.2%→69.2%；顶级豪强 96.2%→87.0%。
 * 附加赛（掷骰）与 NPC 互打（simWinnerOf）不经此函数，不受影响。 */
function seriesOppStr(game){
  const o=seriesOpponentOf();
  const opp=(o&&o.str)?o.str:6;
  const bump={nba:1.5,cba:2.5,euro:1}[myLeagueKey()]||0;
  return Math.round((opp+bump)*10)/10;
}""", 'seriesOppStr 对手拔高')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('季后赛对抗烈度（对手拔高）已应用：%d -> %d 字符（%+d）' % (orig, len(s), len(s) - orig))
