# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 38：加盟时的球队强度快照回正（v4.27.5）

【问题】游玩反馈：「有玩家在的球队强度立马提升导致容易拿总冠军」。
  排查定位：玩家加盟（转会/选秀/签约/交易）时，S.teamStr 直接取 TEAMS 静态底子
  （如「丹佛掘金 = 9」），比赛引擎拿它当球队强度底盘；但球队的真实实力
  （排名/「查看其他球队」列表/联盟模拟）早已是动态口径 teamStrength
  = 底子×20% + 阵容×80%。两套口径脱节——「底子高、阵容差」的队，玩家加盟后
  比赛底盘凭空高一截（隐藏红利→容易夺冠）；反之「阵容强、底子低」的队玩家吃亏。
  jsdom 预演（同一世界内 · ovr88 · 1 号种子 · N=400，修复前=底子口径 / 修复后=账面口径）：
    掘金（底子 9 / 账面 7.8）  32.0% → 10.3%   （红利收回，变难）
    勇士（底子 8 / 账面 10.0） 11.8% → 50.0%   （原来吃亏，现为「真豪门应有之义」）
    雄鹿（底子 8 / 账面 8.7）  11.3% → 20.3%
    国王（底子 6 / 账面 6.7）   1.5% →  3.0%
  修复后「加盟后的比赛强度 = 该队账面」——与列表里显示的「实力 X.X」完全同尺，
  强队强、弱队弱、可查可解释；「有玩家在的球队强度立马提升」不复存在。

【改法】新增 joinTeamStr(队, 回退值)：在 TEAMS 四联赛里找该队，命中则返回实时
  teamStrength（保留一位小数，与显示一致）；找不到（青训队等）回退原值。
  world 未生成时 teamStrength 自动返回底子（等价旧行为），无降级风险。
  9 处加盟路径（setTeam / 签位交易 / 欧洲 / 自由签 / 转会×2 / 登陆NBA / 选秀×2）
  统一改走 setJoinStr()；ensureState 加老档一次性迁移（_joinV2 标记，幂等）。
  边界：附加赛掷骰 / NPC 互打 / 模拟器不受影响——只动「玩家加盟那一刻的快照取值」。
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


# ═══════════ 1. 新增 joinTeamStr / setJoinStr ═══════════
sub1("""function teamStrength(lg,team,base){
  const rs=rosterStr(lg,team);
  if(rs==null)return base;
  return clamp((base||6)*.2+rs*.8,2,11);
}
function leagueKey()""",
     """function teamStrength(lg,team,base){
  const rs=rosterStr(lg,team);
  if(rs==null)return base;
  return clamp((base||6)*.2+rs*.8,2,11);
}
/* v4.27.5 加盟强度快照：取该队「当前阵容实力」（与「查看其他球队」列表/排名同口径）。
 * 旧版直接取 TEAMS 静态底子，与动态阵容脱节——「有玩家在的球队强度立马提升」：
 * 底子高而阵容差的队，玩家加盟后比赛底盘凭空高一截（隐藏红利）。现在加盟即取账面，
 * 强队强、弱队弱，与列表里显示的实力值完全同尺；world 未生成时自动回退底子（等价旧行为）。 */
function joinTeamStr(team,fallback){
  if(!team)return fallback||6;
  for(const lg of ['nba','cba','euro','ncaa']){
    const row=(TEAMS[lg]||[]).find(x=>x[0]===team);
    if(row)return Math.round(teamStrength(lg,team,row[1])*10)/10;
  }
  return fallback||6;
}
function setJoinStr(team,fallback){S.teamStr=joinTeamStr(team,fallback);S._joinV2=1;}
function leagueKey()""", 'joinTeamStr 工具')

# ═══════════ 2. 九处加盟路径统一改走 setJoinStr ═══════════
sub1("['setTeam',(v,c,fx)=>{S.team=v;S.teamStr=fx.setStr||6;",
     "['setTeam',(v,c,fx)=>{S.team=v;setJoinStr(v,fx.setStr);", 'setTeam')

sub1("S.team=to;const tt=TEAMS[lg].find(x=>x[0]===to);S.teamStr=tt?tt[1]:6;S.ts=3;",
     "S.team=to;const tt=TEAMS[lg].find(x=>x[0]===to);setJoinStr(to,tt?tt[1]:6);S.ts=3;", 'tradeYouForPicks')

sub1("const t=R.pick(TEAMS.euro);S.team=t[0];S.teamStr=t[1];S.league='欧洲';",
     "const t=R.pick(TEAMS.euro);S.team=t[0];setJoinStr(t[0],t[1]);S.league='欧洲';", 'rollEuro')

sub1("const t=R.pick(TEAMS.cba.slice(8));S.team=t[0];S.teamStr=t[1];S.league='CBA';",
     "const t=R.pick(TEAMS.cba.slice(8));S.team=t[0];setJoinStr(t[0],t[1]);S.league='CBA';", 'freeCBA')

sub1("S.team=t[0];S.teamStr=t[1];S.ts=3;setContract(S.team,S.league,2,'转会合同');S.starter=starterScore()>=68;",
     "S.team=t[0];setJoinStr(t[0],t[1]);S.ts=3;setContract(S.team,S.league,2,'转会合同');S.starter=starterScore()>=68;", 'rollTrans strong')

sub1("S.team=t[0];S.teamStr=t[1];setContract(S.team,S.league,2,'转会合同');S.starter=starterScore()>=66;",
     "S.team=t[0];setJoinStr(t[0],t[1]);setContract(S.team,S.league,2,'转会合同');S.starter=starterScore()>=66;", 'rollTrans abroad')

sub1("['joinNBA',(v,c)=>{const t=v;S.team=t[0];S.teamStr=t[1];",
     "['joinNBA',(v,c)=>{const t=v;S.team=t[0];setJoinStr(t[0],t[1]);", 'joinNBA')

sub1("""    const mt=(TEAMS.cba.find(x=>x[0]===team)||[,'6'])[1];
    S.team=team;S.teamStr=mt;S.league='CBA';S.ts=3;S.value=baseValue();""",
     """    const mt=(TEAMS.cba.find(x=>x[0]===team)||[,'6'])[1];
    S.team=team;setJoinStr(team,mt);S.league='CBA';S.ts=3;S.value=baseValue();""", 'CBA 选秀入队')

sub1("S.team=team;S.teamStr=mt;S.league='NBA';S.ts=2;S.value=baseValue();",
     "S.team=team;setJoinStr(team,mt);S.league='NBA';S.ts=2;S.value=baseValue();", 'NBA 选秀入队')

# ═══════════ 3. 老档一次性迁移 ═══════════
sub1("""  S.worldNews=S.worldNews||[];
  S.mode=S.mode||'immersive';""",
     """  S.worldNews=S.worldNews||[];
  /* v4.27.5：老档的 teamStr 是「静态底子」→ 一次性升级为当前阵容账面（与新加盟口径一致） */
  if(!S._joinV2&&S.team&&S.teamStr!=null){S.teamStr=joinTeamStr(S.team,S.teamStr);S._joinV2=1;}
  S.mode=S.mode||'immersive';""", 'ensureState 迁移')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('加盟强度快照回正已应用：%d -> %d 字符（%+d）' % (orig, len(s), len(s) - orig))
