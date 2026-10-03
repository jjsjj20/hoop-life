# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 10：签位资产板 + 球队间签位交易（P3.1 / v4.11.0）

在 v4.9.3 的真实签位系统（战绩倒序 + 加权乐透）之上，把签位从「单向流程」变成
「可交易资产」：

  · 签位资产板 ensurePickBoard()：NBA / CBA 每队未来 3 年的首轮 + 次轮签，
    每枚签 = {y, r, orig(槽位原队), owner(现持有方), prot(前 N 保护 | null)}。
    不变量：同 (联赛, 年, 轮, 原队) 的签全联盟恰好一枚。
  · 交易截止日：worldDeadline() 里 AI 球队间真实成交 1~2 笔签位交易（新闻可见）；
    玩家可间接参与——①建议球队送出未来首轮换即战力（pickForHelp），
    ②重建队用未来首轮换走玩家本人（tradeYouForPicks，条件触发）。
  · 选秀夜：draftOwnership() 按资产板解析每个槽位的实际归属并播报；
    被保护的签若落在保护区内 → 归还原队（受让方获次轮签/现金补偿）。
    保护触发 = 槽位序号（0 起，战绩最差在前）< prot。

保护条款语义（刻意简化，遵守计划验收「被保护的签位归还原队」）：
  触保即归还原队，不跨年顺延——受让方改获原队今年次轮签（若原队仍持有），
  否则现金补偿。这样 (年,轮,原队) 唯一性在任意交易序列下都不破。
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


# ═══════════ 1. 核心函数（挂在 doDraft 之前）═══════════
NEW_FUNCS = """/* ── 签位资产板（v4.11 P3.1）：每队未来 3 年首轮/次轮，可交易、带保护 ── */
function curDraftYear(){return S.birthYear+S.age;}   /* 当前赛季对应的选秀年（6 月） */
function ensurePickBoard(){
  S.pickBoard=S.pickBoard||{};
  const D=curDraftYear();
  ['nba','cba'].forEach(lg=>{
    const b=S.pickBoard[lg]=S.pickBoard[lg]||{assets:[]};
    (TEAMS[lg]||[]).forEach(t=>{const orig=t[0];
      for(let r=1;r<=2;r++)for(let k=0;k<3;k++){
        const y=D+k;
        if(!b.assets.some(a=>a.y===y&&a.r===r&&a.orig===orig))
          b.assets.push({y,r,orig,owner:orig,prot:null});
      }
    });
    b.assets=b.assets.filter(a=>a.y>=D);   /* 过期年份清理（随赛季自然滚动） */
  });
  return S.pickBoard;
}
function pickAssetOf(lg,y,r,orig){const b=S.pickBoard&&S.pickBoard[lg];return b?(b.assets.find(a=>a.y===y&&a.r===r&&a.orig===orig)||null):null;}
function slotOwnedBy(lg,y,orig,r){const a=pickAssetOf(lg,y,r,orig);return (a&&a.owner)||orig;}
/* 成交一笔签位交易：只能转手「自己拥有」的签——这是不变量的第一道闸 */
function execPickTrade(lg,fromTeam,toTeam,a){
  const t=pickAssetOf(lg,a.y,a.r,a.orig);
  if(!t||t.owner!==fromTeam||fromTeam===toTeam)return null;
  t.owner=toTeam;return t;
}
function pickName(a){return (a.y<=curDraftYear()?'今年':(a.y-curDraftYear())+'年后')+(a.r===1?'首轮签':'次轮签')+'（'+a.orig+'）';}
/* AI 球队间的签位交易：截止日成交 1~2 笔，新闻可见 */
function aiPickTrades(news){
  try{
    ensurePickBoard();
    ['nba','cba'].forEach(lg=>{
      const D=curDraftYear();
      const n=R.chance(.6)?2:1;
      for(let i=0;i<n;i++){
        const b=S.pickBoard[lg];
        const cands=b.assets.filter(a=>a.y>D&&a.owner===a.orig);
        if(!cands.length)continue;
        const a=R.pick(cands);
        const teams=TEAMS[lg].map(t=>t[0]).filter(t=>t!==a.owner&&t!==a.orig);
        if(!teams.length)continue;
        const to=R.pick(teams);
        if(a.r===1)a.prot=R.int(1,10);   /* 未来首轮带保护：烂队送签自保 */
        const from=a.owner;
        if(!execPickTrade(lg,from,to,a))continue;
        news.push('🔁 签位交易：'+from+' 将 '+pickName(a)+(a.prot?('（前'+a.prot+'保护）'):'')+' 送至 '+to);
      }
    });
  }catch(e){}
}
/* 选秀夜：按资产板解析首轮每个槽位的实际归属（含保护回退），一次结算整晚 */
function draftOwnership(lg,order,year){
  ensurePickBoard();
  return order.map((orig,i)=>{
    const a=pickAssetOf(lg,year,1,orig)||{orig,owner:orig,prot:null};
    let owner=a.owner,reverted=false,comp='';
    if(a.owner!==a.orig&&a.prot!=null&&i<a.prot){
      const buyer=a.owner;
      a.owner=a.orig;owner=a.orig;reverted=true;
      const c=pickAssetOf(lg,year,2,orig);
      if(c&&c.owner===a.orig){c.owner=buyer;comp='，获 '+orig+' 今年次轮签作补偿';}
      else comp='，获现金补偿';
    }
    return {slot:i+1,orig,owner,reverted,comp,prot:a.prot,team:owner};
  });
}
function doDraft(kind,changes){"""
sub1("function doDraft(kind,changes){", NEW_FUNCS, '核心函数插入')

# ═══════════ 2. CBA 选秀：按归属选队 + 播报 ═══════════
sub1("""    const cm=draftOrderOf('cba');
    const team=teamAtPick(cm.order,pick);
    const mt=(TEAMS.cba.find(x=>x[0]===team)||[,'6'])[1];""",
"""    const cm=draftOrderOf('cba');
    const cbaR1=pick<=20;
    const slotTeam=teamAtPick(cm.order,pick);
    const so=cbaR1?draftOwnership('cba',cm.order,curDraftYear())[pick-1]:null;
    const team=so?so.team:slotOwnedBy('cba',curDraftYear(),slotTeam,2);
    const mt=(TEAMS.cba.find(x=>x[0]===team)||[,'6'])[1];""", 'CBA 选秀按归属选队')
sub1("""    changes.push('🎙️ 第 '+pick+' 顺位：'+team+' 选择了 '+S.name+'！'+(pick<=20?'（首轮）':'（次轮）'));""",
"""    changes.push('🎙️ 第 '+pick+' 顺位：'+team+' 选择了 '+S.name+'！'+(pick<=20?'（首轮）':'（次轮）'));
    if(so&&so.orig!==so.owner)changes.push('📋 该签原属 '+so.orig+(so.reverted?('（前'+so.prot+'保护触发，归还原队'+so.comp+'）'):('，由 '+so.owner+' 交易持有')));""", 'CBA 归属播报')

# ═══════════ 3. NBA 选秀：按归属选队 + 播报 ═══════════
sub1("""  const team=teamAtPick(d.order,pick);
  const mt=(TEAMS.nba.find(x=>x[0]===team)||[,'5'])[1];
  const r1=pick<=30;""",
"""  const r1=pick<=30;
  const own1=draftOwnership('nba',d.order,curDraftYear());   /* 首轮全槽位归属，整晚一次结算 */
  const slotTeam=teamAtPick(d.order,pick);
  const so=r1?own1[pick-1]:null;
  const team=so?so.team:slotOwnedBy('nba',curDraftYear(),slotTeam,2);
  const mt=(TEAMS.nba.find(x=>x[0]===team)||[,'5'])[1];""", 'NBA 选秀按归属选队')
sub1("""  d.pick=pick;
  const cls=genDraftClass();
  changes.push('🎙️ 第 '+pick+' 顺位：'+team+' 选择了 '+S.name+'！'+(r1?'（首轮秀）':'（次轮秀）'));""",
"""  d.pick=pick;
  const cls=genDraftClass();
  changes.push('🎙️ 第 '+pick+' 顺位：'+team+' 选择了 '+S.name+'！'+(r1?'（首轮秀）':'（次轮秀）'));
  if(so&&so.orig!==so.owner)changes.push('📋 该签原属 '+so.orig+(so.reverted?('（前'+so.prot+'保护触发，归还原队'+so.comp+'）'):('，由 '+so.owner+' 交易持有')));""", 'NBA 归属播报')
sub1("""  changes.push('本届前三：'+d.order[0]+'选中 '+cls[0].n+'；'+d.order[1]+'选中 '+cls[1].n+'；'+d.order[2]+'选中 '+cls[2].n);""",
"""  changes.push('本届前三：'+own1.slice(0,3).map((o,ix)=>o.team+'选中 '+cls[ix].n+(o.orig!==o.owner?(o.reverted?'（'+o.orig+' 的签，保护触发归还）':'（'+o.orig+' 的签，交易获得）'):'')).join('；'));""", '本届前三按归属播报')

# ═══════════ 4. 交易截止日：AI 成交 + 玩家参与 ═══════════
sub1("""  fixRosterAll();
  S.worldNews=(S.worldNews||[]).concat(news);
}""",
"""  fixRosterAll();
  aiPickTrades(news);   /* v4.11：签位也是资产——截止日 AI 球队间真实成交 */
  S.worldNews=(S.worldNews||[]).concat(news);
}""", 'worldDeadline 挂载签位交易')
sub1("""  if(R.chance(.5))chs.push({t:'有球队询价：提出交易申请',fx:{rollTrans:'strong',clutch:1},o:'他的经纪人放出了交易许可。几支球队递来了报价。'});
  else chs.push({t:'公开表态：我只想留队',fx:{ts:2,stability:1},o:'发布会上，他的回答让主场球迷彻底安心。'});""",
"""  if(R.chance(.5))chs.push({t:'有球队询价：提出交易申请',fx:{rollTrans:'strong',clutch:1},o:'他的经纪人放出了交易许可。几支球队递来了报价。'});
  else chs.push({t:'公开表态：我只想留队',fx:{ts:2,stability:1},o:'发布会上，他的回答让主场球迷彻底安心。'});
  chs.push({t:'建议送出未来首轮签，换即战力',fx:{pickForHelp:1,ts:1},o:'管理层被说服了——用未来赌现在，要慎重，但值得。'});
  if(R.chance(.35)&&ovr()>=68)chs.push({t:'重建队询价：球队想用你换未来签位',fx:{tradeYouForPicks:1},o:'总经理摊牌了：球队需要未来，而你是最好的筹码。'});""", '截止日新增玩家签位选择')

# ═══════════ 5. FX 注册：两个新键 ═══════════
sub1("""  ['makeTrade',(v,c)=>{const r=userTrade();if(r&&r.in){c.push('交易：得到 '+r.in+(r.out?('，送出 '+r.out):''));S.log.push({y:seasonLabel(),t:'截止日交易：得到 '+r.in+(r.out?('，送出 '+r.out):'')});}}],""",
"""  ['makeTrade',(v,c)=>{const r=userTrade();if(r&&r.in){c.push('交易：得到 '+r.in+(r.out?('，送出 '+r.out):''));S.log.push({y:seasonLabel(),t:'截止日交易：得到 '+r.in+(r.out?('，送出 '+r.out):'')});}}],
  /* v4.11 P3.1：签位交易（玩家间接参与） */
  ['pickForHelp',(v,c)=>{ensurePickBoard();const lg=myLeagueKey();
    if(lg!=='nba'&&lg!=='cba'){c.push('该联赛没有选秀签位，无从交易');return;}
    const D=curDraftYear();const a=pickAssetOf(lg,D+1,1,myTeamName());
    if(!a||a.owner!==myTeamName()){const r0=userTrade();c.push('球队手里没有可动的未来首轮签，改为直接补强'+(r0&&r0.in?('：得到 '+r0.in):''));return;}
    const teams=TEAMS[lg].map(t=>t[0]).filter(t=>t!==myTeamName());
    const to=R.pick(teams);a.prot=R.int(1,10);
    execPickTrade(lg,myTeamName(),to,a);
    ensureWorld();const nm=lg==='cba'?genCN():genWest();
    S.world[lg].push({n:nm,p:R.pick(Object.keys(POS)),o:R.int(74,84),a:R.int(26,32),t:myTeamName(),ts:S.teamStr||6,role:'start'});fixRosterAll();
    c.push('📦 '+myTeamName()+' 将 '+pickName(a)+'（前'+a.prot+'保护）送至 '+to+'，换来即战力 '+nm);
    S.log.push({y:seasonLabel(),t:'签位交易：送出'+pickName(a)+'，得到 '+nm});}],
  ['tradeYouForPicks',(v,c)=>{ensurePickBoard();const lg=myLeagueKey();
    if(lg!=='nba'&&lg!=='cba'){c.push('该联赛没有选秀签位，无从交易');return;}
    const D=curDraftYear();const oldTeam=S.team;
    const pool=TEAMS[lg].slice(0,6).map(t=>t[0]).filter(t=>t!==oldTeam);
    const to=R.pick(pool.length?pool:TEAMS[lg].map(t=>t[0]).filter(t=>t!==oldTeam));
    const a=pickAssetOf(lg,D+1,1,to);
    if(a&&a.owner===to){a.prot=null;execPickTrade(lg,to,oldTeam,a);}   /* 我队收下对方的未来首轮 */
    S.team=to;const tt=TEAMS[lg].find(x=>x[0]===to);S.teamStr=tt?tt[1]:6;S.ts=3;
    if(!S.played.includes(S.team))S.played.push(S.team);
    setContract(S.team,S.league,2,'转会合同');
    c.push('📦 交易达成：'+oldTeam+' 将你送至 '+to+'，换回'+(a?' '+pickName(a):'未来资产')+'。新球队的发布会上，总经理说：「我们盯了你很久。」');
    S.log.push({y:seasonLabel(),t:'被交易至 '+to+'（换回签位资产）'});}],""", 'FX 注册 pickForHelp/tradeYouForPicks')
sub1("""  ['end',()=>{}],          /* 生涯终结（退役/转教练）：advance() 中处理 */""",
"""  ['end',()=>{}],          /* 生涯终结（退役）：advance() 中处理 */""", '清理转教练遗留注释')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('签位交易已应用：%d -> %d 字符（%+d）' % (orig, len(s), len(s) - orig))
