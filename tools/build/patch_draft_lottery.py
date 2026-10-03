# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 6：真实签位系统（战绩倒序 + 加权乐透）

旧实现的问题：
    function nbaDraftOrder(){
      const arr=TEAMS.nba.map(t=>[t[0],t[1]*10+R.int(0,9)]);   // ← 按「静态球队实力」排
      arr.sort((a,b)=>a[1]-b[1]);
      const lotto=arr.slice(0,6);                              // ← 乐透只有 6 队
      for(...) { 洗牌 }                                        // ← 而且等概率乱序
      return lotto.concat(arr.slice(6)).map(x=>x[0]);
    }
也就是既没用上赛季战绩（球队底子强=签位低，跟谁上赛季打得多差无关），
乐透区也不对（6 队等概率 vs 现实 14 队加权），还只抽 6 签。

按现实规则重做：
  NBA（2019 现行）
    · 14 支未进季后赛球队进乐透区，按常规赛战绩倒序拿状元签概率
      14.0/14.0/14.0/12.5/10.5/9.0/7.5/6.0/4.5/3.0/2.0/1.5/1.0/0.5 %
    · 只抽前 4 签（抽中不放回，等价于按概率逐签无放回抽样）
    · 第 5-14 签：剩下的乐透球队按战绩倒序
    · 第 15-30 签：16 支季后赛球队按常规赛战绩倒序（季后赛走多远不影响签位，这是现实规则）
    · 第 31-60 签与首轮同序
  CBA（2020 现行）
    · 8 支未进季后赛球队进乐透区，状元签概率按常规赛倒数 1-8 名
      22/19/17/14/11/8/6/3 %
    · 只抽前 3 签（状元 / 榜眼 / 探花）；第 4 顺位起按战绩倒序

顺带修掉一个旧行为：签位原本一旦生成就永久复用（换年不重抽），
现在按赛季标记，新赛季重新抽签。
"""
import os

BASE = os.path.dirname(os.path.abspath(__file__))
HTML = os.environ.get('GAME_HTML') or os.path.join(BASE, '..', 'output', '篮球人生.html')

s = open(HTML, encoding='utf-8').read()
orig = len(s)


def sub1(old, new, why):
    n = s.count(old)
    if n != 1:
        raise SystemExit('!! %s 匹配 %d 次' % (why, n))
    return s.replace(old, new)


# ═══════════ 1. 抽签引擎 ═══════════
OLD_ORDER = """function nbaDraftOrder(){
  const arr=TEAMS.nba.map(t=>[t[0],t[1]*10+R.int(0,9)]);
  arr.sort((a,b)=>a[1]-b[1]);
  const lotto=arr.slice(0,6);
  for(let i=lotto.length-1;i>0;i--){const j=R.int(0,i);const tmp=lotto[i];lotto[i]=lotto[j];lotto[j]=tmp;}
  return lotto.concat(arr.slice(6)).map(x=>x[0]);
}
function cbaDraftOrder(){
  return TEAMS.cba.map(t=>[t[0],t[1]*10+R.int(0,9)]).sort((a,b)=>a[1]-b[1]).map(x=>x[0]);
}
function ensureDraft(){
  if(!S.draft)S.draft={stock:draftStockInit(),order:nbaDraftOrder(),promise:null,pick:null,y:seasonLabel()};
  if(!S.draft.order||S.draft.order.length!==TEAMS.nba.length)S.draft.order=nbaDraftOrder();
  if(typeof S.draft.stock!=='number'||!Number.isFinite(S.draft.stock))S.draft.stock=draftStockInit();
  return S.draft;
}"""

NEW_ORDER = """/* ---- v4.9.3 真实签位：战绩倒序 + 加权乐透 ----
 * 签位只认「上赛季常规赛战绩」，不认球队底子强不强——底子好但上赛季伤兵满营打崩了，
 * 就该拿到高顺位。乐透区按现实规则加权抽签，而不是等概率乱序。 */
const NBA_LOTTO_ODDS=[14.0,14.0,14.0,12.5,10.5,9.0,7.5,6.0,4.5,3.0,2.0,1.5,1.0,0.5];
const CBA_LOTTO_ODDS=[22,19,17,14,11,8,6,3];
const LOTTO_RULES={
  nba:{teams:'nba',nLot:14,nDraw:4,odds:NBA_LOTTO_ODDS,slot:['状元签','榜眼签','探花签','第四顺位']},
  cba:{teams:'cba',nLot:8,nDraw:3,odds:CBA_LOTTO_ODDS,slot:['状元签','榜眼签','探花签']}
};
/* 上赛季常规赛战绩，战绩最差的排最前。
 * 同战绩用随机数拆开先后（现实里是抛硬币决定选秀顺序）。 */
function standingsWorstFirst(lg){
  let rows=null;
  try{rows=computeStandings(lg);}catch(e){rows=null;}
  if(!rows||!rows.length){
    /* 兜底：拿不到战绩就退回按球队实力排，绝不因此崩掉选秀 */
    return (TEAMS[lg]||[]).map(t=>({team:t[0],str:t[1],wins:0}))
      .sort((a,b)=>a.str-b.str);
  }
  return rows.map(r=>({team:r.team,str:r.str,wins:r.wins||0,_t:R.float(0,1)}))
    .sort((x,y)=>x.wins-y.wins||x._t-y._t);
}
/* 按概率逐签无放回抽样 —— 等价于现场「抽中不放回、抽到重复队就重抽」的小球抽签 */
function lotteryDraw(order,odds,n){
  const pool=order.map((t,i)=>({team:t,w:Math.max(0,Number(odds[i])||0)}));
  const win=[];
  for(let k=0;k<n&&pool.length;k++){
    let tot=0;for(let i=0;i<pool.length;i++)tot+=pool[i].w;
    if(tot<=0)break;
    let r=R.float(0,tot),hit=pool.length-1;
    for(let i=0;i<pool.length;i++){r-=pool[i].w;if(r<=0){hit=i;break;}}
    win.push(pool[hit].team);
    pool.splice(hit,1);
  }
  return {win,left:pool.map(x=>x.team)};
}
/* 生成一届完整签位表：乐透抽中的前 N 签 + 剩余乐透队（战绩倒序）+ 季后赛队（战绩倒序） */
function draftOrderOf(lg){
  const cfg=LOTTO_RULES[lg]||LOTTO_RULES.nba;
  const st=standingsWorstFirst(cfg.teams);
  const lotto=st.slice(0,cfg.nLot),rest=st.slice(cfg.nLot);
  const lottoTeams=lotto.map(x=>x.team);
  const oddsOf={};lottoTeams.forEach((t,i)=>{oddsOf[t]=cfg.odds[i]||0;});
  const r=lotteryDraw(lottoTeams,cfg.odds,cfg.nDraw);
  return {
    lg:lg,order:r.win.concat(r.left).concat(rest.map(x=>x.team)),
    /* draw 只用于展示：抽中的顺位 + 该队抽签前的状元签概率 */
    draw:r.win.map(t=>({team:t,p:oddsOf[t]||0})),
    lotto:lottoTeams,
    slot:cfg.slot,
    playoff:rest.map(x=>x.team)
  };
}
function nbaDraftOrder(){return draftOrderOf('nba').order;}
function cbaDraftOrder(){return draftOrderOf('cba').order;}
/* 抽签结果文案（选秀夜 / 落选后回 CBA 时都会用到） */
function lottoText(draw,slot){
  if(!draw||!draw.length)return '';
  const nm=slot||['状元签','榜眼签','探花签','第四顺位'];
  return '本届乐透抽签：'+draw.map((x,i)=>(nm[i]||('第'+(i+1)+'签'))+' '+x.team+'（'+
    (Math.round(Number(x.p)*10)/10).toString().replace(/\\.0$/,'')+'%）').join(' · ');
}
function ensureDraft(){
  if(!S.draft)S.draft={stock:draftStockInit(),order:null,draw:null,lotto:null,promise:null,pick:null,y:null};
  /* 签位按赛季重抽：旧实现一旦生成就永久复用，换一年还是同一张签位表 */
  if(!S.draft.order||S.draft.order.length!==TEAMS.nba.length||S.draft.y!==seasonLabel()){
    const m=draftOrderOf('nba');
    S.draft.order=m.order;S.draft.draw=m.draw;S.draft.lotto=m.lotto;S.draft.slot=m.slot;S.draft.y=seasonLabel();
  }
  if(typeof S.draft.stock!=='number'||!Number.isFinite(S.draft.stock))S.draft.stock=draftStockInit();
  return S.draft;
}"""

s = sub1(OLD_ORDER, NEW_ORDER, '替换签位生成逻辑')

# ═══════════ 2. 选秀夜把抽签结果摆给玩家看 ═══════════
OLD_NIGHT = """  const prom=(d.promise&&d.promise.team)?('经纪人的手机又亮了：'+d.promise.team+' 的号码——他们昨晚刚来过电话。'):'';"""
NEW_NIGHT = """  const prom=(d.promise&&d.promise.team)?('经纪人的手机又亮了：'+d.promise.team+' 的号码——他们昨晚刚来过电话。'):'';
  /* v4.9.3：乐透抽签结果先亮一次——签位顺序不再是黑箱 */
  const lotto=lottoText(d.draw,d.slot);"""
s = sub1(OLD_NIGHT, NEW_NIGHT, '选秀夜取出抽签文案')

OLD_NIGHT_SCENE = """return {id:'draftNight',title:'夏 · 选秀夜',scene:'选秀夜。'"""
NEW_NIGHT_SCENE = """return {id:'draftNight',title:'夏 · 选秀夜',scene:'选秀夜。'+(lotto?(lotto+'。\\n\\n'):'')"""
s = sub1(OLD_NIGHT_SCENE, NEW_NIGHT_SCENE, '选秀夜正文插入抽签结果')

# ═══════════ 3. CBA 通道也用新签位表，并亮出抽签结果 ═══════════
OLD_CBA_PICK = """    const team=teamAtPick(cbaDraftOrder(),pick);
    const mt=(TEAMS.cba.find(x=>x[0]===team)||[,'6'])[1];"""
NEW_CBA_PICK = """    const cm=draftOrderOf('cba');
    const team=teamAtPick(cm.order,pick);
    const mt=(TEAMS.cba.find(x=>x[0]===team)||[,'6'])[1];"""
s = sub1(OLD_CBA_PICK, NEW_CBA_PICK, 'CBA 用新签位表')

OLD_CBA_CH = """    changes.push('🎙️ 第 '+pick+' 顺位：'+team+' 选择了 '+S.name+'！'+(pick<=20?'（首轮）':'（次轮）'));"""
NEW_CBA_CH = """    changes.push('🎙️ 第 '+pick+' 顺位：'+team+' 选择了 '+S.name+'！'+(pick<=20?'（首轮）':'（次轮）'));
    changes.push(lottoText(cm.draw,cm.slot));"""
s = sub1(OLD_CBA_CH, NEW_CBA_CH, 'CBA 播报抽签结果')

# ═══════════ 4. NBA 播报补一条签位背景 ═══════════
OLD_NBA_CH = """  if(pick<=14)changes.push('🏅 乐透秀！全家的欢呼把房间淹没。');"""
NEW_NBA_CH = """  if(pick<=14)changes.push('🏅 乐透秀！全家的欢呼把房间淹没。');
  if(d.draw&&d.draw.length&&pick!==1)changes.push('🎯 '+lottoText(d.draw,d.slot));"""
s = sub1(OLD_NBA_CH, NEW_NBA_CH, 'NBA 播报抽签结果')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('真实签位系统已应用：%d -> %d 字符（+%d）' % (orig, len(s), len(s) - orig))
