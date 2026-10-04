# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 14：P7 签位玩法延伸 + computeStandings 缓存修复（v4.14.0）

P7 三件套（资产板地基 v4.11.0 已就位，延伸都便宜）：
  ① 资产板可视化：showPickAssets() 覆盖层——我队未来 3 年首轮/次轮的
     归属与保护一览（自持 / 已交易至 X（触保归我）/ 从 Y 获得），行动栏新增「📋 签位」按钮；
  ② 顺位互换：execSwap() + aiPickTrades 三成半概率走互换线——
     两队交换明年首轮签，保护条款各自保留，新闻播报「互换权交易」；
  ③ 保签摆烂事件：我队未来首轮已被交易且带前 N（≥3）保护时，
     冬季阶段可能触发「管理层的暗示」抉择——摆烂的收益（触保回退）
     由选秀夜的保护机制自然兑现，事件只负责把这个处境讲出来。

computeStandings 缓存修复（已知问题清单 ⚪ 单槽缓存项）：
  旧版 S._stCache 是单槽（仅 lg+赛季键），换联赛查看会把另一联赛的缓存顶掉，
  同一赛季同一联赛反复重摇 → 排名前后不一致。改为按联赛分槽：
  S._stCache[lg]={season,rows}；旧形状单槽缓存读入时一次性迁移清空。
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


# ═══════════ 1. computeStandings：单槽 → 按联赛分槽 ═══════════
sub1("""  const _sy=seasonLabel();
  if(S._stCache&&S._stCache.lg===lg&&S._stCache.season===_sy&&Array.isArray(S._stCache.rows)&&S._stCache.rows.length){
    return S._stCache.rows.map(r=>Object.assign({},r));
  }""",
"""  const _sy=seasonLabel();
  /* v4.14：单槽缓存升级为按联赛分槽——旧版换联赛查看会把另一联赛的缓存顶掉，
   * 同一赛季同一联赛反复重摇，排名前后不一致（已知问题清单的「单槽缓存」项）。 */
  if(S._stCache&&S._stCache.rows)S._stCache={};   /* 旧形状单槽缓存一次性迁移 */
  S._stCache=S._stCache||{};
  const _hit=S._stCache[lg];
  if(_hit&&_hit.season===_sy&&Array.isArray(_hit.rows)&&_hit.rows.length){
    return _hit.rows.map(r=>Object.assign({},r));
  }""", '缓存读取分槽')
sub1("""  S._stCache={lg:lg,season:seasonLabel(),rows:rows.map(r=>Object.assign({},r))};""",
"""  S._stCache[lg]={season:seasonLabel(),rows:rows.map(r=>Object.assign({},r))};""", '缓存写入分槽')

# ═══════════ 2. 保签摆烂：条件 + 事件 + SPECIAL_RULES 挂载 ═══════════
sub1("""const SPECIAL_RULES=[""",
"""/* v4.14 P7 保签摆烂：我队的未来首轮已被交易、且带前 N（≥3）保护时，
 * 管理层可能暗示「摆烂换回签位」——触保回退的收益由选秀夜的保护机制自然兑现。 */
function tankScenarioReady(){
  if(S.league!=='NBA'&&S.league!=='CBA')return false;
  if(S.stage!=='winter')return false;
  if(S.flags['tank'+(S.birthYear+S.age)])return false;
  ensurePickBoard();
  const a=pickAssetOf(myLeagueKey(),curDraftYear()+1,1,S.team);
  if(!a||a.owner===S.team||!(a.prot>=3))return false;
  return R.chance(.4);
}
function evTankHint(){
  ensurePickBoard();
  const a=pickAssetOf(myLeagueKey(),curDraftYear()+1,1,S.team)||{prot:'N'};
  return {id:'tankHint',title:'冬 · 管理层的暗示',scene:`总经理在走廊里拦住${S.name}，话里有话：「明年那支前${a.prot}保护的首轮签，本来是我们的。战绩这个东西……你懂的。」赛季还长，「摆烂」两个字第一次被摆上了明面。`,choices:[
    ch('拒绝：我们每一场都想赢',{clutch:2,ts:1},'他当着教练组把话挑明。那场比赛球队赢了——用行动回答比用嘴回答有力。'),
    ch('默许轮换：给年轻人让路',{stability:-2,ts:-1,hustle:1},'他开始打起了「养生篮球」。年轻人的上场时间涨了，他的数据落了。'),
    ch('装作没听懂',{stability:1},'他笑着点了点头，转头照常训练。有些话，装听不见也是一种回答。')
  ]};
}
const SPECIAL_RULES=[""", '摆烂事件前置函数')
sub1("""  /* 季前训练营：每年秋天三选一，给赛季一个起跑姿势 */
  [()=>S.age>=16&&S.stage==='autumn'&&!S.flags['camp'+(S.birthYear+S.age)],
    ()=>{S.flags['camp'+(S.birthYear+S.age)]=true;return evCamp();}],""",
"""  /* 季前训练营：每年秋天三选一，给赛季一个起跑姿势 */
  [()=>S.age>=16&&S.stage==='autumn'&&!S.flags['camp'+(S.birthYear+S.age)],
    ()=>{S.flags['camp'+(S.birthYear+S.age)]=true;return evCamp();}],
  /* v4.14 保签摆烂：我队未来首轮已被交易且带高保护 → 冬季可能触发管理层暗示 */
  [()=>tankScenarioReady(),
    ()=>{S.flags['tank'+(S.birthYear+S.age)]=true;return evTankHint();}],""", 'SPECIAL_RULES 挂载摆烂事件')

# ═══════════ 3. 顺位互换：execSwap + aiPickTrades 互换分支 ═══════════
sub1("""/* AI 球队间的签位交易：截止日成交 1~2 笔，新闻可见 */""",
"""/* 顺位互换（v4.14 P7）：两队交换各自持有的明年首轮签，保护条款各自保留。
 * 与两笔独立交易不同——互换是同时成交的一笔交易，任一侧不成立则整笔作废。 */
function execSwap(lg,a,b){
  const x=pickAssetOf(lg,a.y,a.r,a.orig),y=pickAssetOf(lg,b.y,b.r,b.orig);
  if(!x||!y||x.owner!==a.owner||y.owner!==b.owner)return null;
  if(a.orig===b.orig||a.owner===b.owner)return null;
  x.owner=b.owner;y.owner=a.owner;
  return [x,y];
}
/* AI 球队间的签位交易：截止日成交 1~2 笔，新闻可见 */""", 'execSwap 前置')
sub1("""        const b=S.pickBoard[lg];
        const cands=b.assets.filter(a=>a.y>D&&a.owner===a.orig);
        if(!cands.length)continue;
        const a=R.pick(cands);
        const teams=TEAMS[lg].map(t=>t[0]).filter(t=>t!==a.owner&&t!==a.orig);
        if(!teams.length)continue;
        const to=R.pick(teams);
        if(a.r===1)a.prot=R.int(1,10);   /* 未来首轮带保护：烂队送签自保 */
        const from=a.owner;
        if(!execPickTrade(lg,from,to,a))continue;
        news.push('🔁 签位交易：'+from+' 将 '+pickName(a)+(a.prot?('（前'+a.prot+'保护）'):'')+' 送至 '+to);""",
"""        const b=S.pickBoard[lg];
        const own=b.assets.filter(a=>a.y>D&&a.owner===a.orig&&a.r===1);
        /* v4.14：三成半概率走「顺位互换」——两队交换明年首轮，保护各自保留 */
        if(own.length>=2&&R.chance(.35)){
          const a=R.pick(own);
          const b2=R.pick(own.filter(x=>x.orig!==a.orig&&x.owner!==a.orig));
          const done=b2?execSwap(lg,a,b2):null;
          if(done)news.push('🔁 互换权交易：'+a.orig+' 与 '+b2.orig+' 互换明年首轮签（保护条款各自保留）');
          continue;
        }
        const a=R.pick(own);
        const teams=TEAMS[lg].map(t=>t[0]).filter(t=>t!==a.owner&&t!==a.orig);
        if(!teams.length)continue;
        const to=R.pick(teams);
        if(a.r===1)a.prot=R.int(1,10);   /* 未来首轮带保护：烂队送签自保 */
        const from=a.owner;
        if(!execPickTrade(lg,from,to,a))continue;
        news.push('🔁 签位交易：'+from+' 将 '+pickName(a)+(a.prot?('（前'+a.prot+'保护）'):'')+' 送至 '+to);""", 'aiPickTrades 互换分支')

# ═══════════ 4. 资产板可视化：showPickAssets + 行动栏按钮 ═══════════
sub1("""/* 💼 财务：收入 / 消费 / 投资 / 训练投入（钱要能花出去） */""",
"""/* 📋 我的签位资产（v4.14 P7）：未来 3 年首轮/次轮的归属与保护一览 */
function showPickAssets(){
  if(S.league!=='NBA'&&S.league!=='CBA'){
    openOvl(`<h3>📋 签位资产</h3><div class="mini">该联赛没有选秀签位，无从交易。</div><button class="btn ghost" style="margin-top:14px" onclick="closeOvl()">关闭</button>`);
    return;
  }
  ensurePickBoard();
  const lg=myLeagueKey(),D=curDraftYear();
  const mine=S.pickBoard[lg].assets.filter(a=>a.orig===S.team||a.owner===S.team)
    .sort((a,b)=>a.y-b.y||a.r-b.r);
  const desc=a=>{
    const y=(a.y===D?'今年':(a.y-D)+'年后')+(a.r===1?'首轮':'次轮');
    if(a.owner===a.orig)return y+' · 自持'+(a.prot!=null?' · 前'+a.prot+'保护':'');
    if(a.orig===S.team)return y+' · 已交易至 '+a.owner+(a.prot!=null?'（前'+a.prot+'保护，触保归我）':'');
    return y+'（来自 '+a.orig+'）· 我队持有'+(a.prot!=null?' · 前'+a.prot+'保护':'');
  };
  const rows=mine.map(a=>'<div class="row"><span>'+desc(a)+'</span><b>'+(a.owner===S.team?'我方':'对方')+'</b></div>').join('');
  openOvl(`<h3>📋 签位资产 · ${esc(S.team)}</h3><div class="mini">${esc(LEAGUE_NAMES[S.league]||S.league)} · 未来 3 年首轮/次轮归属（截止日交易与选秀夜实时变动）</div><div class="summ">${rows||'<div class="mini">暂无签位资产记录</div>'}</div><button class="btn ghost" style="margin-top:14px" onclick="closeOvl()">关闭</button>`);
}
/* 💼 财务：收入 / 消费 / 投资 / 训练投入（钱要能花出去） */""", 'showPickAssets 插入')
sub1("""     ${(S.league==='CBA'||S.league==='NBA'||S.league==='欧洲')?'<button onclick="showStandings()">📊 排名</button>':''}""",
"""     ${(S.league==='CBA'||S.league==='NBA'||S.league==='欧洲')?'<button onclick="showStandings()">📊 排名</button><button onclick="showPickAssets()">📋 签位</button>':''}""", '行动栏签位按钮')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('P7 已应用：%d -> %d 字符（%+d）' % (orig, len(s), len(s) - orig))
