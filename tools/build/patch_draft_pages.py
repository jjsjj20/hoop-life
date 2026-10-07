# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 36：NBA 选秀与签位抽签系统（v4.26.0）

用户需求（五条）：
  ① 为 NBA 选秀与 NBA 签位抽签分别创建独立的页面；
  ② 签位抽签结果由各球队的常规赛战绩决定；
  ③ 明确流程顺序——抽签在选秀之前；
  ④ 时间安排在赛季结束之后、新赛季开启之前；
  ⑤ 选中的球员必须出现在该球队的球员名单里。

实现（游戏内两个独立页面）：
  · 修赛期序列：赛季总结页按钮 nextYear() → seasonNext()（仅 NBA、未退役、45 岁前）：
      签位抽签页（mode 'lottery'）→ 选秀大会页（mode 'draftday'）→ nextYear()
  · 抽签页：14 支乐透队按「赛季落幕时缓存的那张战绩表」列战绩与状元签概率，
    展示抽签结果（1-4 签）+ 15-30 顺位摘要；数据源 = draftOrderOf（战绩倒序 + 加权乐透）。
  · 选秀页：60 顺位（两轮）逐签落定——含交易签与保护回退（draftOwnership）；
    选中的新秀即刻写入 S.world.nba 名单（draftSignRookie），并带 rk/pend 新秀标记。
  · 单源真相：draftPlanFor(year) 按年缓存签位表与战绩快照——抽签页/选秀页读同一份。
  · 选秀夜（玩家参选路径）同源升级：doDraft('nba') 用 resolveDraftInto 让本届其余
    顺位也真实落位入队（此前只在文案里播报前三，NPC 不入队）；落选路径同样结算。
  · 新秀标记：worldTick 的 rk 清零改为「新秀首季保留」（pend 标记），被选中的新秀
    入行首季可参评最佳新秀，与 fixRosterAll 顶替新人的口径一致。

边界：CBA/欧洲/NCAA 流程不动；非 NBA 球员的休赛期不出现这两个页面；
玩家参选路径的顺位计算（行情+波动+承诺+cap）不变，只是其余 59 签一起落位。
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


# ═══════════ 1. 选秀班底 → 完整新秀 + 年度计划 + 逐签解析 + 两个页面 ═══════════
sub1("function genDraftClass(){const c=[];for(let i=0;i<59;i++)c.push({n:R.chance(.72)?genWest():genCN(),p:R.pick(Object.keys(POS)),o:R.int(58,86)});return c;}",
"""/* ═══════════ 06.7 NBA 选秀与签位抽签（v4.26.0 · 两个独立页面） ═══════════
 * 流程：赛季落幕 →【签位抽签】14 支乐透队按常规赛战绩拿不同概率抽 1-4 签
 *   →【选秀大会】60 个顺位逐签落定，选中的新秀写入球队名单 → 新赛季开启。
 * 数据关联：一届只有一份签位表（draftPlanFor 按年缓存）——抽签页、选秀页、
 * 选秀夜公告读同一份；页面展示的战绩与抽签用的是同一张战绩表。 */
function draftProspect(){
  const o=R.int(56,80);
  const a=R.int(19,22);
  const room=(a<=20)?R.int(12,30):R.int(8,24);
  return {n:R.chance(.72)?genWest():genCN(),p:R.pick(Object.keys(POS)),o:o,a:a,
    pot:clamp(o+room,o,97),role:'bench',rk:1,pend:1};
}
function draftPlanFor(y){
  S.draftPlans=S.draftPlans||{};
  const key=String(y);
  let p=S.draftPlans[key];
  if(!p||!p.order||p.order.length!==TEAMS.nba.length||!p.draw){
    const m=draftOrderOf('nba');   /* 战绩倒序 + 加权乐透（用当下缓存里的那张战绩表） */
    p={y:key,order:m.order,draw:m.draw,lotto:m.lotto,slot:m.slot,recs:{},resolved:false,picks:null};
    try{computeStandings('nba').forEach(r=>{p.recs[r.team]={w:r.wins,l:r.losses,str:r.str};});}catch(e){}
    S.draftPlans[key]=p;
    Object.keys(S.draftPlans).map(Number).sort((a,b)=>b-a).slice(3).forEach(k=>{delete S.draftPlans[k];});
  }
  return p;
}
/* 选中即入队：新秀写入对应球队名单（需求第 5 条） */
function draftSignRookie(team,pr){
  ensureWorld();
  S.world.nba=S.world.nba||[];
  S.world.nba.push({n:pr.n,p:pr.p,o:pr.o,a:pr.a,pot:pr.pot,t:team,
    ts:((TEAMS.nba.find(x=>x[0]===team)||[,'6'])[1]),role:'bench',rk:1,pend:1});
}
/* 逐签解析一届选秀：60 顺位（两轮）全部落位——含交易签与保护回退；
 * 班底先按行情排序（能力 + 潜力 + 噪音），最好的新秀先被选走；
 * 玩家参选时把玩家插在第 myPick 位，其余顺位由班底补齐。 */
function resolveDraftInto(order,myPick,me){
  const y=curDraftYear();
  ensurePickBoard();
  const own1=draftOwnership('nba',order,y);
  const cls=[];
  for(let i=0;i<60;i++)cls.push(draftProspect());
  cls.forEach(p=>{p._sc=p.o+p.pot*.5+R.float(-6,6);});
  cls.sort((a,b)=>b._sc-a._sc);
  cls.forEach(p=>{delete p._sc;});
  const picks=[];
  let j=0;
  for(let i=1;i<=60;i++){
    const slotTeam=teamAtPick(order,i);
    const r1=i<=30;
    const so=r1?own1[i-1]:null;
    const team=so?so.team:slotOwnedBy('nba',y,slotTeam,2);
    if(me&&myPick===i){
      picks.push({pick:i,team:team,orig:slotTeam,owner:team,reverted:!!(so&&so.reverted),
        n:me.name,p:me.pos,o:me.ovr,a:me.age,me:true});
    }else{
      const pr=cls[j++];
      draftSignRookie(team,pr);
      picks.push({pick:i,team:team,orig:slotTeam,owner:team,reverted:!!(so&&so.reverted),n:pr.n,p:pr.p,o:pr.o,a:pr.a});
    }
  }
  return {y:y,picks:picks};
}
/* 休赛期序列：赛季页「进入下一年」先走两个页面（仅 NBA），再真进下一年 */
function seasonNext(){
  if(!S.retired&&S.league==='NBA'&&S.age<45){
    const plan=draftPlanFor(curDraftYear());
    if(!plan.resolved){UI={mode:'lottery',dy:plan.y};save();renderGame();return;}
  }
  nextYear();
}
function goDraftDay(){
  const plan=S.draftPlans&&S.draftPlans[String(UI.dy)];
  if(!plan){nextYear();return;}
  if(!plan.resolved){
    plan.picks=resolveDraftInto(plan.order,null,null).picks;
    plan.resolved=true;save();
  }
  UI={mode:'draftday',dy:plan.y};save();renderGame();
}
/* ① 签位抽签页：乐透区 14 队的战绩 × 状元签概率 × 抽签结果 */
function renderLottery(){
  const plan=S.draftPlans&&S.draftPlans[String(UI.dy)];
  const box=$('#stage');
  if(!plan){box.innerHTML='<div class="mini">选秀计划数据缺失。</div><button class="btn" onclick="nextYear()">继续 ▶</button>';return;}
  const slot=plan.slot||['状元签','榜眼签','探花签','第四顺位'];
  const myT=myTeamName();
  const rec=t=>{const r=plan.recs&&plan.recs[t];return r?(r.w+'胜'+r.l+'负'):'—';};
  const rows=plan.order.slice(0,14).map((t,i)=>
    '<div class="tr'+(t===myT?' me':'')+'"><span class="rk'+(i<3?(' g'+(i+1)):'')+'">'+(i+1)+'</span>'+
    '<span class="tm">'+crestOf(t)+esc(t)+(t===myT?' （你）':'')+'</span>'+
    '<span class="rec">'+rec(t)+'</span>'+
    '<span class="pb"><i style="width:'+Math.round(NBA_LOTTO_ODDS[plan.lotto.indexOf(t)]||0)+'%"></i></span>'+
    (i<4?('<span class="tg gold">'+slot[i]+'</span>'):'')+'</div>').join('');
  const rest=plan.order.slice(14,30);
  box.innerHTML='<div class="etitle">🎱 六月 · 选秀抽签大会</div>'+
  '<div class="summ"><h3>乐透区 · 14 队</h3>'+
  '<div class="mini">战绩越差 → 状元签概率越高；抽签结果决定第 1-14 号签的归属。</div>'+
  rows+
  '<div class="mini" style="margin-top:8px">15-30 号签：未进乐透的 16 队按战绩倒序——'+
  rest.map((t,i)=>((i+15)+'.'+esc(t))).join('　')+'</div></div>'+
  '<div class="summ"><h3>抽签结果</h3>'+
  plan.draw.map((d,i)=>'<div class="row"><span>'+['🥇 状元签','🥈 榜眼签','🥉 探花签','4️⃣ 第四顺位'][i]+'</span><b>'+esc(d.team)+'（'+Math.round(d.p*10)/10+'% 概率命中）</b></div>').join('')+
  '<div class="mini">接下来：各队在选秀大会上按这份签位表挑选新秀。</div></div>'+
  '<button class="btn" onclick="goDraftDay()">前往选秀大会 ▶</button>';
}
/* ② 选秀大会页：60 顺位逐签结果 + 新秀入队播报 */
function renderDraftDay(){
  const plan=S.draftPlans&&S.draftPlans[String(UI.dy)];
  const box=$('#stage');
  if(!plan||!plan.resolved||!plan.picks){box.innerHTML='<div class="mini">本届选秀尚未结算。</div><button class="btn" onclick="nextYear()">继续 ▶</button>';return;}
  const myT=myTeamName();
  const line=p=>{const mine=p.team===myT;
    return '<div class="mini" style="line-height:1.9">'+(mine?'<b style="color:var(--gold)">':'')+
      '#'+p.pick+' <b>'+esc(p.team)+'</b> —— '+esc(p.n)+' <span style="opacity:.65">'+p.p+' · 综合 '+p.o+' · '+p.a+'岁</span>'+(mine?'（你队）</b>':'')+'</div>';};
  const top3=plan.picks.slice(0,3);
  box.innerHTML='<div class="etitle">🎓 六月 · 选秀大会</div>'+
  '<div class="summ"><h3>前三顺位</h3>'+
  top3.map((p,i)=>'<div class="row"><span>'+['🥇 状元','🥈 榜眼','🥉 探花'][i]+'</span><b>'+esc(p.team)+' —— '+esc(p.n)+'（'+p.p+' · '+p.o+'）</b></div>').join('')+
  '<div class="mini">60 个顺位全部落定；被选中的新秀已经进入对应球队的名单。</div></div>'+
  '<div class="summ"><h3>首轮（1-30）</h3>'+plan.picks.slice(0,30).map(line).join('')+'</div>'+
  '<div class="summ"><h3>次轮（31-60）</h3>'+plan.picks.slice(30,60).map(line).join('')+'</div>'+
  '<button class="btn" onclick="nextYear()">休赛期结束 · 进入下一年 ▶</button>';
}""",
     '选秀班底与两个页面')

# ═══════════ 2. 赛季页按钮：先走抽签/选秀，再进下一年 ═══════════
sub1('<button class="btn" onclick="nextYear()">进入下一年 · 春 ▶</button>',
     '<button class="btn" onclick="seasonNext()">进入下一年 · 春 ▶</button>',
     '赛季页按钮')

# ═══════════ 3. 新秀标记：入行首季保留参评资格 ═══════════
sub1("      p.rk=0;                  /* 上赛季的新秀今年不再参评最佳新秀（fixRosterAll 会给新补进来的人打标） */",
     """      /* v4.26.0：刚通过选秀入行的新秀（pend 标记）首季保留参评资格，其余照旧清零 */
      p.rk=p.pend?1:0;p.pend=0;""",
     'worldTick 新秀标记')

# ═══════════ 4. 选秀夜：落选路径也结算本届全部顺位 ═══════════
sub1("""  if(pick>60){
    S.flags.undrafted=true;
    changes.push('第二轮结束，他的名字依然没有被念到……');""",
     """  if(pick>60){
    S.flags.undrafted=true;
    resolveDraftInto(d.order);   /* v4.26.0：落选不影响本届其余顺位照常落位入队 */
    changes.push('第二轮结束，他的名字依然没有被念到……');""",
     '落选路径结算')

# ═══════════ 5. 选秀夜：玩家被选中时，其余顺位一起落位 ═══════════
sub1("  const cls=genDraftClass();",
     "  const _dr=resolveDraftInto(d.order,pick,{name:S.name,pos:S.pos,ovr:o,age:S.age});   /* v4.26.0：本届全部顺位落定，新秀入队 */",
     '玩家参选结算')

# ═══════════ 6. 本届前三：改用真实落位结果 ═══════════
sub1("  changes.push('本届前三：'+own1.slice(0,3).map((o,ix)=>o.team+'选中 '+cls[ix].n+(o.orig!==o.owner?(o.reverted?'（'+o.orig+' 的签，保护触发归还）':'（'+o.orig+' 的签，交易获得）'):'')).join('；'));",
     "  changes.push('本届前三：'+_dr.picks.slice(0,3).map(x=>x.team+'选中 '+x.n+((x.orig!==x.owner)?(x.reverted?'（'+x.orig+' 的签，保护触发归还）':'（'+x.orig+' 的签，交易获得）'):'')).join('；'));",
     '本届前三改用真实结果')

# ═══════════ 7. renderGame 模式分派：两个新页面 ═══════════
sub1("      case 'end':showEnd();break;",
     """      case 'lottery':renderLottery();break;
      case 'draftday':renderDraftDay();break;
      case 'end':showEnd();break;""",
     'renderGame 分派')

# ═══════════ 8. 读档恢复：新页面模式纳入保护分支 ═══════════
sub1("      if(UI&&(UI.mode==='season'||UI.mode==='awards')){S.stage='winter';}",
     "      if(UI&&(UI.mode==='season'||UI.mode==='awards'||UI.mode==='lottery'||UI.mode==='draftday')){S.stage='winter';}",
     '读档保护分支')

# ═══════════ 9. 选秀系统头注同步 ═══════════
sub1(" * ⑤落选判定与行情挂钩；⑥选秀班底 59 人，播报本届前三。 */",
     " * ⑤落选判定与行情挂钩；⑥选秀班底 60 人（两轮）——签位抽签与选秀大会为独立页面，新秀真实入队（v4.26.0）。 */",
     '选秀头注')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('NBA 选秀与签位抽签系统已应用：%d -> %d 字符（%+d）' % (orig, len(s), len(s) - orig))
