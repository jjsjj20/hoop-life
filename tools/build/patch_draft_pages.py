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

【v4.26.1】游玩反馈「NBA 选秀中的中国人太多了」：班底名字构成从 28% 中国名
  （每届约 17 人）降到 4%（每届约 1~3 人）——NBA 背景以欧美球员为主。

【v4.26.2】游玩反馈「想要名单一个一个出」：两个页面改为逐位揭晓——
  抽签：从状元签开始点一次揭一位（？？？→球队），四签揭完才排定 1-14 与按钮；
  选秀：从第 1 顺位开始逐位宣布（最新的在最上面），另给「直接看完全部」跳过；
  揭晓进度（UI.lr / UI.dr）随存档保存，中途退出回来接着出。

【v4.27.0】游玩反馈「玩家的 NBA 选秀也加入这个系统」：玩家参选走同一套仪式——
  · 签位表单源化：newDraft / ensureDraft 改读 draftPlanFor（与联盟选秀同一份），
    玩家的抽签结果 = 联盟的抽签结果，不再各掷各的；
  · 选秀夜流程：点「等待命运的宣判」→【抽签揭牌页】→【选秀大会逐位念名】
    → 念到玩家顺位定格（fanfare）或 60 位念完（落选）→ 恢复原结果页（合同等）；
  · 仪式数据挂在 UI.crm（含原事件与 changes），随存档持久化可续；
  · 选秀夜夜景与结果页不再重复播报乐透抽签（改由揭牌页呈现）。

【v4.27.1】游玩反馈「选秀导致联盟实力膨胀」。15 年世界演化探针实测（每年 60 人注入 +
  nextYear 全流程）：平铺 56~80 + 大潜力房（均值 ~87）把联盟从 73.2 灌到 86.1（+12.9）、
  30 队实力全部顶死在 9.75（天花板）。两轮对照实验结论：
    · 主因 = 入口潜力均值（均衡值 ≈ 班底潜力均值×0.55 + 36.6），与「留队价值的选择
      偏差」无关（削弱选择后 +5.55 / 纯能力裁员 +6.91，反而更胀）；
    · 修复 = 班底整体降格 + 按顺位加权（E2 版）：o=40+(58−pick)×0.55±5、潜力房
      8~22（≤20 岁）/5~16——潜力均值 ~68 → 15 年漂移 +0.35，联盟稳定在既有水平；
    · 顺带收益：状元签期望最高、二轮尾是落选级，比平铺更真实；resolveDraftInto
      不再需要「按行情排序」，直接按顺位生成（与探针口径逐字一致）。

【v4.27.2】游玩反馈两条：
  ① 「玩家还没被选中就已经显示球队」——doDraft 在仪式前写入 S.team，顶栏/侧栏/
     合同一直在剧透。修复：选秀夜暂存 S._preDraft，仪式未念到名字前 myTeamName/
     teamLabel/contractLabel/renderTop 全部按原球队口径显示（crmMaskOn /
     dispTeam 统一遮盖），finishDraftCeremony 清除暂存。
  ② 「玩家综合 72 结果 35 顺位，NPC 综合 70 结果 6 顺位」——旧行情档位表是按
     「平铺班底」校准的，与按顺位加权的新班底不同尺。修复：draftStockInit 改为
     班底曲线逆函数 58-(o-40)/0.55 + 年龄修正（无随机），综合直接决定期望顺位。

【v4.27.3】游玩反馈「新秀第一个赛季结束之后不会显示选秀与签位抽签」：
  根因=键冲突——玩家参选年份与「新秀赛季结束后的休赛期」同岁（年龄在赛季末才 +1），
  seasonNext 取 draftPlanFor(curDraftYear()) 命中了参选年已被仪式 resolved 的计划，
  两个页面被整段吞掉。修复：联盟页面改用「下一届」键 curDraftYear()+1（每届一键、
  永不复用）；resolveDraftForPlan 改为显式传计划（参选路径传参选年键、联盟传 UI.dy 计划）。
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
function draftProspect(pick){
  /* v4.27.1 平衡：按顺位加权 + 整体降格。老版平铺 56~80、潜力均值 ~87 会把联盟
   * 15 年灌到平均能力 86 / 30 队实力全部顶格（探针实测 +12.9）——均衡值 ≈ 班底
   * 潜力均值×0.55+36.6，本版潜力均值 ~68 → 15 年漂移 +0.35，停在既有水平。
   * 而「留队价值的选择偏差」经对照实验证明不是主因，未动。 */
  const pk=clamp(pick||30,1,60);
  const o=clamp(Math.round(40+(58-pk)*0.55+R.float(-5,5)),38,84);
  const a=R.int(19,22);
  const room=(a<=20)?R.int(8,22):R.int(5,16);
  /* 名字构成（v4.26.1）：NBA 选秀班底以欧美球员为主，中国面孔约 4%——
   * 每届 60 人里 1~3 位中国新秀，偶尔出现，符合现实观感。 */
  return {n:R.chance(.96)?genWest():genCN(),p:R.pick(Object.keys(POS)),o:o,a:a,
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
 * 班底按顺位生成（v4.27.1：状元签期望最高、二轮尾是落选级，不再整体排序）；
 * 玩家参选时把玩家插在第 myPick 位，其余顺位由班底补齐。 */
function resolveDraftInto(order,myPick,me){
  const y=curDraftYear();
  ensurePickBoard();
  const own1=draftOwnership('nba',order,y);
  const picks=[];
  for(let i=1;i<=60;i++){
    const slotTeam=teamAtPick(order,i);
    const r1=i<=30;
    const so=r1?own1[i-1]:null;
    const team=so?so.team:slotOwnedBy('nba',y,slotTeam,2);
    if(me&&myPick===i){
      picks.push({pick:i,team:team,orig:slotTeam,owner:team,reverted:!!(so&&so.reverted),
        n:me.name,p:me.pos,o:me.ovr,a:me.age,me:true});
    }else{
      const pr=draftProspect(i);
      draftSignRookie(team,pr);
      picks.push({pick:i,team:team,orig:slotTeam,owner:team,reverted:!!(so&&so.reverted),n:pr.n,p:pr.p,o:pr.o,a:pr.a});
    }
  }
  return {y:y,picks:picks};
}
/* 结算本届并把结果写回年度计划（v4.27.0：玩家选秀夜与联盟选秀共用同一份；
 * v4.27.3：支持显式传入计划——联盟页面按「下一届」键取计划，不再依赖默认键） */
function resolveDraftForPlan(plan,myPick,me){
  const p=plan||draftPlanFor(curDraftYear());
  const r=resolveDraftInto(p.order,myPick,me);
  p.picks=r.picks;p.resolved=true;
  return r;
}
/* v4.27.2 防剧透：选秀仪式（UI.crm）在念到玩家名字之前，对外仍显示原球队——
 * 顶栏/侧栏/阵容/合同全部走这三个helper，doDraft 提前写入的新球队不外泄。 */
function crmRevealed(){
  if(!UI||!UI.crm)return true;
  const plan=S.draftPlans&&S.draftPlans[String(UI.dy)];
  if(!plan||!plan.picks)return true;
  const meP=plan.picks.filter(p=>p.me)[0];
  return meP?((UI.dr||0)>=meP.pick):((UI.dr||0)>=plan.picks.length);
}
function crmMaskOn(){return !!(UI&&UI.crm&&!crmRevealed());}
function dispTeam(){const p=crmMaskOn()?S._preDraft:null;return p?{team:(p.team||'待定'),league:p.league}:{team:(S.team||'待定'),league:S.league};}
/* 休赛期序列：赛季页「进入下一年」先走两个页面（仅 NBA），再真进下一年 */
function seasonNext(){
  if(!S.retired&&S.league==='NBA'&&S.age<45){
    /* v4.27.3：用「下一届」键（+1）——玩家参选年份与「新秀赛季结束后的休赛期」
     * 同岁（年龄在赛季末才 +1），同键会命中参选年已 resolved 的计划、把页面吞掉；
     * +1 后每一届各有一个键，永不复用。 */
    const plan=draftPlanFor(curDraftYear()+1);
    if(!plan.resolved){UI={mode:'lottery',dy:plan.y,lr:0};save();renderGame();return;}
  }
  nextYear();
}
function goDraftDay(){
  const plan=S.draftPlans&&S.draftPlans[String(UI.dy)];
  if(!plan){nextYear();return;}
  if(!plan.resolved){
    resolveDraftForPlan(plan);save();
  }
  UI={mode:'draftday',dy:plan.y,dr:0,crm:UI.crm||null};save();renderGame();
}
/* 逐位揭晓（v4.26.2）：抽签从状元签开始一个个揭牌；选秀从第 1 顺位一个个念 */
function revealLottery(){
  const plan=S.draftPlans&&S.draftPlans[String(UI.dy)];
  if(!plan)return;
  if((UI.lr||0)<plan.draw.length){UI.lr=(UI.lr||0)+1;try{sfx('draft');}catch(e){}}
  save();renderGame();
}
function revealPick(){
  const plan=S.draftPlans&&S.draftPlans[String(UI.dy)];
  if(!plan||!plan.picks)return;
  if(UI.dr==null)UI.dr=0;
  const meP=UI.crm?(plan.picks.filter(p=>p.me)[0]||null):null;
  const cap=meP?meP.pick:plan.picks.length;
  if(UI.dr<cap){UI.dr++;try{sfx(meP&&UI.dr===meP.pick?'fanfare':'draft');}catch(e){}}
  save();renderGame();
}
function revealAllPicks(){
  const plan=S.draftPlans&&S.draftPlans[String(UI.dy)];
  if(!plan||!plan.picks)return;
  const meP=UI.crm?(plan.picks.filter(p=>p.me)[0]||null):null;
  UI.dr=meP?meP.pick:plan.picks.length;save();renderGame();
}
/* 仪式收尾（v4.27.0）：回到选秀夜原本的结果页（合同 / 顺位播报 / 落选文案都在 changes 里）；
 * v4.27.2：同时清掉防剧透暂存——对外恢复显示新球队。 */
function finishDraftCeremony(){
  const c=UI&&UI.crm;
  S._preDraft=null;
  if(!c||!c.ev){UI={mode:'event',ev:safeEvent()};save();renderGame();return;}
  UI={mode:'result',ev:c.ev,chIdx:c.chIdx,changes:c.changes};
  save();renderGame();
}
/* ① 签位抽签页：从状元签开始逐一揭牌（？？？→球队），揭完四签才排定 1-14 */
function renderLottery(){
  const plan=S.draftPlans&&S.draftPlans[String(UI.dy)];
  const box=$('#stage');
  if(!plan){box.innerHTML='<div class="mini">选秀计划数据缺失。</div><button class="btn" onclick="nextYear()">继续 ▶</button>';return;}
  if(UI.lr==null)UI.lr=0;
  const slot=plan.slot||['状元签','榜眼签','探花签','第四顺位'];
  const myT=myTeamName();
  const done=UI.lr>=plan.draw.length;
  const rec=t=>{const r=plan.recs&&plan.recs[t];return r?(r.w+'胜'+r.l+'负'):'—';};
  /* 揭榜区：状元签 → 第四顺位，点一次出一位 */
  const drawRows=plan.draw.map((d,i)=>'<div class="row"><span>'+['🥇 状元签','🥈 榜眼签','🥉 探花签','4️⃣ 第四顺位'][i]+'</span><b>'+
    (i<UI.lr?(esc(d.team)+'（'+Math.round(d.p*10)/10+'% 概率命中）'):'？？？')+'</b></div>').join('');
  /* 乐透区表：始终按「战绩倒序（机会大小）」排；全部揭晓后再标注最终顺位 */
  const pickOf={};plan.order.slice(0,14).forEach((t,i)=>{pickOf[t]=i+1;});
  const rows=plan.lotto.map((t,i)=>
    '<div class="tr'+(t===myT?' me':'')+'"><span class="rk'+(done&&pickOf[t]<=3?(' g'+pickOf[t]):'')+'">'+(done?pickOf[t]:(i+1))+'</span>'+
    '<span class="tm">'+crestOf(t)+esc(t)+(t===myT?' （你）':'')+'</span>'+
    '<span class="rec">'+rec(t)+'</span>'+
    '<span class="pb"><i style="width:'+Math.round(NBA_LOTTO_ODDS[i]||0)+'%"></i></span>'+
    (done?('<span class="tg gold">'+(pickOf[t]<=4?slot[pickOf[t]-1]:('第'+pickOf[t]+'顺位'))+'</span>'):'')+'</div>').join('');
  const rest=plan.order.slice(14,30);
  box.innerHTML='<div class="etitle">🎱 六月 · 选秀抽签大会</div>'+
  '<div class="summ"><h3>抽签现场</h3>'+drawRows+
  (done?'<div class="mini">抽签完毕——第 1-14 号签的归属已全部排定。</div>'
       :'<div class="mini">从状元签开始，点一次揭晓一位。</div>')+'</div>'+
  '<div class="summ"><h3>乐透区 · 14 队（按战绩倒序 · 机会大小）</h3>'+rows+
  '<div class="mini" style="margin-top:8px">15-30 号签：未进乐透的 16 队按战绩倒序——'+
  rest.map((t,i)=>((i+15)+'.'+esc(t))).join('　')+'</div></div>'+
  (done?'<button class="btn" onclick="goDraftDay()">前往选秀大会 ▶</button>'
       :'<button class="btn" onclick="revealLottery()">揭晓'+slot[UI.lr]+' ▶</button>');
}
/* ② 选秀大会页：从第 1 顺位开始逐位宣布；最新的在最上面，可选「直接看完全部」。
 * v4.27.0：仪式模式（UI.crm）下念到玩家顺位即定格，按钮切「继续」回结果页。 */
function renderDraftDay(){
  const plan=S.draftPlans&&S.draftPlans[String(UI.dy)];
  const box=$('#stage');
  if(!plan||!plan.resolved||!plan.picks){box.innerHTML='<div class="mini">本届选秀尚未结算。</div><button class="btn" onclick="nextYear()">继续 ▶</button>';return;}
  if(UI.dr==null)UI.dr=0;
  const myT=myTeamName();
  const all=plan.picks;
  const crm=UI.crm||null;
  const meP=crm?(all.filter(p=>p.me)[0]||null):null;
  const stop=meP?meP.pick:all.length;
  const done=UI.dr>=stop;
  const line=p=>{const mine=(crm&&p.me)||p.team===myT;
    return '<div class="mini" style="line-height:1.9">'+(mine?'<b style="color:var(--gold)">':'')+
      '#'+p.pick+' <b>'+esc(p.team)+'</b> —— '+esc(p.n)+' <span style="opacity:.65">'+p.p+' · 综合 '+p.o+' · '+p.a+'岁</span>'+(p.me?'（就是你！）':(mine?'（你队）':''))+(mine?'</b>':'')+'</div>';};
  let body;
  if(done){
    if(crm){
      body='<div class="summ"><h3>'+(meP?('🎙️ 第 '+meP.pick+' 顺位：'+esc(meP.team)+' 选择了你！'):'两轮念完，没有念到他')+'</h3>'+
      (meP?'':'<div class="mini">接下来是另一条路——训练、试训，或者回联赛再打回来。</div>')+
      all.slice(0,stop).map(line).join('')+'</div>';
    }else{
      body='<div class="summ"><h3>前三顺位</h3>'+
      all.slice(0,3).map((p,i)=>'<div class="row"><span>'+['🥇 状元','🥈 榜眼','🥉 探花'][i]+'</span><b>'+esc(p.team)+' —— '+esc(p.n)+'（'+p.p+' · '+p.o+'）</b></div>').join('')+
      '<div class="mini">60 个顺位全部落定；被选中的新秀已经进入对应球队的名单。</div></div>'+
      '<div class="summ"><h3>首轮（1-30）</h3>'+all.slice(0,30).map(line).join('')+'</div>'+
      '<div class="summ"><h3>次轮（31-60）</h3>'+all.slice(30,60).map(line).join('')+'</div>';
    }
  }else{
    const latest=all.slice(0,UI.dr).reverse();
    body='<div class="summ"><h3>已公布 '+UI.dr+(crm?' 位':' / '+all.length+' 位')+'</h3>'+
    (latest.length?latest.map(line).join(''):'<div class="mini">选秀大会开始——点下面的按钮，逐一宣布今年的新秀。</div>')+'</div>';
  }
  box.innerHTML='<div class="etitle">🎓 六月 · 选秀大会</div>'+body+
  (done?(crm?'<button class="btn" onclick="finishDraftCeremony()">继续 ▶</button>'
             :'<button class="btn" onclick="nextYear()">休赛期结束 · 进入下一年 ▶</button>')
       :'<button class="btn" onclick="revealPick()">宣布第 '+(UI.dr+1)+' 顺位 ▶</button>'+
        '<button class="btn ghost" onclick="revealAllPicks()">'+(meP?'直接看我的顺位':'直接看完全部 '+all.length+' 位')+'</button>');
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

# ═══════════ 10. 玩家参选单源化：newDraft / ensureDraft 读年度计划 ═══════════
sub1("""function newDraft(){
  const m=draftOrderOf('nba');
  return {stock:draftStockInit(),order:m.order,draw:m.draw,lotto:m.lotto,slot:m.slot,
          promise:null,pick:null,y:seasonLabel()};
}""",
     """function newDraft(){
  const plan=draftPlanFor(curDraftYear());   /* v4.27.0：与联盟选秀共用同一份年度签位表 */
  return {stock:draftStockInit(),order:plan.order,draw:plan.draw,lotto:plan.lotto,slot:plan.slot,
          promise:null,pick:null,y:seasonLabel()};
}""",
     'newDraft 单源化')

sub1("""  if(!S.draft.order||S.draft.order.length!==TEAMS.nba.length||S.draft.y!==seasonLabel()||!S.draft.draw){
    const m=draftOrderOf('nba');
    S.draft.order=m.order;S.draft.draw=m.draw;S.draft.lotto=m.lotto;S.draft.slot=m.slot;S.draft.y=seasonLabel();
  }""",
     """  if(!S.draft.order||S.draft.order.length!==TEAMS.nba.length||S.draft.y!==seasonLabel()||!S.draft.draw){
    const plan=draftPlanFor(curDraftYear());   /* v4.27.0：与联盟选秀共用同一份年度签位表 */
    S.draft.order=plan.order;S.draft.draw=plan.draw;S.draft.lotto=plan.lotto;S.draft.slot=plan.slot;S.draft.y=seasonLabel();
  }""",
     'ensureDraft 单源化')

# ═══════════ 11. 选秀夜结算写回年度计划 + 去掉重复播报 ═══════════
sub1("    resolveDraftInto(d.order);   /* v4.26.0：落选不影响本届其余顺位照常落位入队 */",
     "    resolveDraftForPlan(draftPlanFor(curDraftYear()));   /* v4.27.3：显式传计划（参选年键） */",
     '落选写回')

sub1("  const _dr=resolveDraftInto(d.order,pick,{name:S.name,pos:S.pos,ovr:o,age:S.age});   /* v4.26.0：本届全部顺位落定，新秀入队 */",
     "  const _dr=resolveDraftForPlan(draftPlanFor(curDraftYear()),pick,{name:S.name,pos:S.pos,ovr:o,age:S.age});   /* v4.27.3：显式传计划（参选年键） */",
     '玩家结算写回')

sub1("  if(pick!==1){const _lt=lottoText(d.draw,d.slot);if(_lt)changes.push('🎯 '+_lt);}",
     "  /* v4.27.0：乐透抽签改由「抽签揭晓页」逐个揭牌，结果页不再重复播报 */",
     '去重播报')

# ═══════════ 12. 选秀夜夜景：不提前剧透抽签结果 ═══════════
sub1("""  /* v4.9.3：乐透抽签结果先亮一次——签位顺序不再是黑箱 */
  const lotto=lottoText(d.draw,d.slot);
  return {id:'draftNight',title:'夏 · 选秀夜',scene:'选秀夜。'+(lotto?(lotto+'。\\n\\n'):'')+(green?""",
     """  /* v4.27.0：乐透抽签改由「抽签揭晓页」逐个揭牌，夜景不再提前剧透 */
  return {id:'draftNight',title:'夏 · 选秀夜',scene:'选秀夜。'+(green?""",
     '夜景去剧透')

# ═══════════ 13. choose() 尾钩子：选秀夜 → 仪式两页 → 结果页 ═══════════
sub1("""  UI={mode:'result',ev,chIdx:i,changes};
  renderResult(ev,i,changes);save();
}
/* 一份季后赛结果的唯一构造点（v4.12 P4.2）。""",
     """  /* v4.27.0：玩家 NBA 选秀夜 → 先进「抽签揭牌 → 选秀大会」两个揭晓页，结果页最后再出 */
  if(ch0&&ch0.fx&&ch0.fx.rollDraft==='nba'){
    const _dp=draftPlanFor(curDraftYear());
    if(_dp&&_dp.picks&&_dp.picks.length){
      UI={mode:'lottery',dy:_dp.y,lr:0,crm:{ev:ev,chIdx:i,changes:changes}};
      save();renderGame();return;
    }
  }
  UI={mode:'result',ev,chIdx:i,changes};
  renderResult(ev,i,changes);save();
}
/* 一份季后赛结果的唯一构造点（v4.12 P4.2）。""",
     '仪式钩子')

# ═══════════ 14. v4.27.2：行情与班底同尺（综合决定顺位）═══════════
sub1("""function draftStockInit(){
  const o=ovr(),age=S.age;let base;
  /* v4.23.0 选秀门槛整体后移：同评分段的行情普遍差 4~12 位——NBA 不再是
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
  else base=R.float(61,76);
  base+=age>=23?8:age>=22?5:age>=21?2:0;
  if(age<=19)base-=2;
  return clamp(Math.round(base),1,72);
}""",
     """function draftStockInit(){
  /* v4.27.2：行情与班底同尺——班底曲线 o(pick)=40+(58-pick)×0.55 的逆函数：
   * 综合 o 的期望顺位 ≈ 58-(o-40)/0.55。旧档位表是按「平铺班底」校准的，
   * 与按顺位加权的新班底对不上（72 综合曾掉到 35 顺位、70 的 NPC 却走 6 顺位）。
   * 试训涨跌/球队承诺/选秀夜噪音/顺位保护照旧。速查：72 ≈ 状元热门区、
   * 64 ≈ 首轮中段、56 ≈ 次轮、≤43 ≈ 落选边缘。 */
  const o=ovr(),age=S.age;
  let base=58-(o-40)/0.55;
  base+=age>=23?4:age>=22?3:age>=21?1:0;
  if(age<=19)base-=1;
  return clamp(Math.round(base),1,72);
}""",
     '选秀行情曲线')

# ═══════════ 15. v4.27.2：仪式防剧透（显示层统一遮盖）═══════════
sub1("function myTeamName(){return S.team;}",
     "function myTeamName(){const p=crmMaskOn()?S._preDraft:null;return p?p.team:S.team;}",
     'myTeamName 遮盖')

sub1("""function teamLabel(){
  if(S.trial)return S.trial.kind==='tenDay'?`${S.trial.team}（10天短合同）`:`${S.trial.team} 发展联盟`;
  return (S.team||'待定')+' · '+LEAGUE_NAMES[S.league];
}""",
     """function teamLabel(){
  if(S.trial)return S.trial.kind==='tenDay'?`${S.trial.team}（10天短合同）`:`${S.trial.team} 发展联盟`;
  const _p=crmMaskOn()?S._preDraft:null;   /* v4.27.2：仪式未揭晓前显示原球队 */
  if(_p)return (_p.team||'待定')+' · '+(LEAGUE_NAMES[_p.league]||'');
  return (S.team||'待定')+' · '+LEAGUE_NAMES[S.league];
}""",
     'teamLabel 遮盖')

sub1("""function contractLabel(){
  if(!S)return '';
  if(S.trial)return S.trial.kind==='tenDay'?'10天短合同':'发展联盟合同';
  if(S.league==='青训')return '青训补贴';
  if(S.league==='NCAA')return '大学奖学金';
  if(!S.contract)return '自由球员';
  return S.contract.team+' · €'+S.contract.wage+'万/年 · 剩'+S.contract.years+'年';
}""",
     """function contractLabel(){
  if(!S)return '';
  if(S.trial)return S.trial.kind==='tenDay'?'10天短合同':'发展联盟合同';
  /* v4.27.2：仪式未揭晓前按原球队口径显示（防剧透） */
  const _p=crmMaskOn()?S._preDraft:null;
  if(_p){
    if(_p.league==='青训')return '青训补贴';
    if(_p.league==='NCAA')return '大学奖学金';
    if(!_p.contract)return '自由球员';
    return _p.contract.team+' · €'+_p.contract.wage+'万/年 · 剩'+_p.contract.years+'年';
  }
  if(S.league==='青训')return '青训补贴';
  if(S.league==='NCAA')return '大学奖学金';
  if(!S.contract)return '自由球员';
  return S.contract.team+' · €'+S.contract.wage+'万/年 · 剩'+S.contract.years+'年';
}""",
     'contractLabel 遮盖')

sub1("  const who={n:S.name,s:`${esc(S.team||'待定')} <span class=\"lg\">${LEAGUE_NAMES[S.league]||''}</span>`,v:ovr(),tag:'🏀 '+POS[S.pos].n.slice(0,2)};",
     """  const _dt=dispTeam();
  const who={n:S.name,s:`${esc(_dt.team)} <span class="lg">${LEAGUE_NAMES[_dt.league]||''}</span>`,v:ovr(),tag:'🏀 '+POS[S.pos].n.slice(0,2)};""",
     'renderTop 遮盖')

sub1("  S.team=team;S.teamStr=mt;S.league='NBA';S.ts=2;S.value=baseValue();\n  if(!S.played.includes(S.team))S.played.push(S.team);\n  const years=r1?4:3;",
     "  S._preDraft={team:S.team,teamStr:S.teamStr,ts:S.ts,league:S.league,contract:S.contract};   /* v4.27.2：仪式期间对外仍显示原球队（防剧透） */\n  S.team=team;S.teamStr=mt;S.league='NBA';S.ts=2;S.value=baseValue();\n  if(!S.played.includes(S.team))S.played.push(S.team);\n  const years=r1?4:3;",
     '选秀夜暂存原球队')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('NBA 选秀与签位抽签系统已应用：%d -> %d 字符（%+d）' % (orig, len(s), len(s) - orig))
