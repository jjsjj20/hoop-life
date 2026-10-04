# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 12：P4 收尾（v4.12.0 / 里程碑 M3「遗留项清零」）

P4.1 放开双指缩放（评审第 4 条遗留，产品决策已拍板）：
  viewport 去掉 maximum-scale=1.0 与 user-scalable=no，保留 viewport-fit=cover（刘海屏）。

P4.2 季后赛结果收敛唯一工厂（同 v4.9.5 newDraft() 的做法，防患不是修 bug）：
  S._playoffResult 此前 7 处各写各的字面量，kind/level 时有时无，消费端全靠兜底；
  收敛成 makePlayoffResult()——字段补成统一形状 {rounds, champ, kind, level}，
  以后加字段不可能只补一半。行为完全等价：'' 与 undefined 在所有消费点
  （r.kind==='xxx' / if(r.kind)）里语义相同。

P4.3 空 catch（73 处）按计划自评「价值低，可长期不动」保留——
  v4.9.5 已逐类核对为刻意收窄的保护，此处记录决策，不改代码。
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


# ═══════════ P4.1 viewport 放开缩放 ═══════════
sub1('<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">',
     '<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">',
     'viewport 放开双指缩放')

# ═══════════ P4.2 季后赛结果唯一工厂 ═══════════
sub1("""function advance(){""",
"""/* 一份季后赛结果的唯一构造点（v4.12 P4.2）。
 * 之前 7 处各写各的对象字面量，kind/level 时有时无——消费端全靠兜底。
 * 收敛成唯一工厂：字段补成统一形状，以后加字段不可能只补一半。
 * 行为等价：'' 与 undefined 在所有消费点（r.kind==='xxx' / if(r.kind)）语义相同。 */
function makePlayoffResult(o){
  return Object.assign({rounds:0,champ:false,kind:'',level:''},o||{});
}
function advance(){""", 'makePlayoffResult 工厂')

sub1("""          S._playoffResult={rounds:3,champ:true,kind:'march'};""",
     """          S._playoffResult=makePlayoffResult({rounds:3,champ:true,kind:'march'});""", '构造点 1/7（疯狂三月夺冠）')
sub1("""          S._playoffResult={rounds:marchStageNo(ev.march)-1,champ:false,level:'march',kind:'march'};""",
     """          S._playoffResult=makePlayoffResult({rounds:marchStageNo(ev.march)-1,champ:false,level:'march',kind:'march'});""", '构造点 2/7（疯狂三月出局）')
sub1("""        if(nx==='champ'||nx==='done'||!nx){S._playoffResult={rounds:3,champ:true};UI={mode:'event',ev:evPlayoffChamp()};}""",
     """        if(nx==='champ'||nx==='done'||!nx){S._playoffResult=makePlayoffResult({rounds:3,champ:true});UI={mode:'event',ev:evPlayoffChamp()};}""", '构造点 3/7（季后赛夺冠）')
sub1("""        S._playoffResult={rounds:(S.playoff&&S.playoff.rounds)||0,champ:false,level:st};""",
     """        S._playoffResult=makePlayoffResult({rounds:(S.playoff&&S.playoff.rounds)||0,champ:false,level:st});""", '构造点 4/7（系列赛出局）')
sub1("""        else{bracketPlayerWin();S._playoffResult={rounds:3,champ:true};UI={mode:'event',ev:evPlayoffChamp()};}""",
     """        else{bracketPlayerWin();S._playoffResult=makePlayoffResult({rounds:3,champ:true});UI={mode:'event',ev:evPlayoffChamp()};}""", '构造点 5/7（对阵图夺冠）')
sub1("""          else{S._playoffResult={rounds:0,champ:false,kind:'playin'};UI={mode:'event',ev:evPlayInExit()};}""",
     """          else{S._playoffResult=makePlayoffResult({rounds:0,champ:false,kind:'playin'});UI={mode:'event',ev:evPlayInExit()};}""", '构造点 6/7（附加赛出局）')
sub1("""        else{S._playoffResult={rounds:(S.playoff&&S.playoff.rounds)||0,champ:false,level:(S.bracket&&S.bracket.currentStage)||'r1'};UI={mode:'event',ev:evPlayoffExit()};}""",
     """        else{S._playoffResult=makePlayoffResult({rounds:(S.playoff&&S.playoff.rounds)||0,champ:false,level:(S.bracket&&S.bracket.currentStage)||'r1'});UI={mode:'event',ev:evPlayoffExit()};}""", '构造点 7/7（首轮出局）')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('P4 收尾已应用：%d -> %d 字符（%+d）' % (orig, len(s), len(s) - orig))
