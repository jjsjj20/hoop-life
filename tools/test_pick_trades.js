/* 签位交易系统（v4.11 P3.1）—— 计划验收第 ⑤ 条：
 * 「模拟 200 次签位交易，断言保护条款生效、签位不重复、不出现同一签位归两队」
 *
 * 签位资产板不变量（任何交易序列之后都必须成立）：
 *   I1  同 (联赛, 年, 轮, 原队) 的签全联盟恰好一枚
 *   I2  每枚签的持有方都是该联盟的真实球队
 *   I3  只能转手「自己拥有」的签（冒名交易必须被拒绝）
 *   I4  保护条款：持有方≠原队 且 槽位序号(0起,战绩最差在前) < 前 N 保护 → 归还原队
 *   I5  归属解析后每个槽位恰好由一支真实球队行使
 */
const { run } = require('./testkit');

module.exports = run('签位交易', ({ win, check }) => {
  win.eval('renderCreate();');
  win.eval("document.getElementById('fName').value='签位测试';");
  win.eval('doCreate(); allocRandom(); confirmAlloc();');
  win.eval("S.league='NBA';S.mode='immersive';S.team=TEAMS.nba[0][0];S.teamStr=6;S.age=21;S.stage='winter';ensureWorld();");

  // ── 1. 资产板结构 ────────────────────────────────
  const st = JSON.parse(win.eval(`JSON.stringify((function(){
    ensurePickBoard();
    const out={teams:{},boards:{},dup:0};
    ['nba','cba'].forEach(function(lg){
      const b=S.pickBoard[lg];const seen={};let d=0;
      b.assets.forEach(function(a){
        const k=a.y+'|'+a.r+'|'+a.orig;if(seen[k])d++;seen[k]=1;
        if(!TEAMS[lg].some(function(t){return t[0]===a.orig;}))d++;
      });
      out.boards[lg]={n:b.assets.length,dup:d};
      out.teams[lg]=TEAMS[lg].length;
    });
    out.D=curDraftYear();
    return out;})())`));
  check('资产板覆盖 NBA/CBA 两联盟', !!(st.boards.nba && st.boards.cba), JSON.stringify(Object.keys(st)));
  check('每联盟资产数 = 队数 × 3 年 × 2 轮',
    st.boards.nba.n === st.teams.nba * 3 * 2 && st.boards.cba.n === st.teams.cba * 3 * 2,
    JSON.stringify(st.boards));
  check('I1 (年,轮,原队) 无重复、原队真实', st.boards.nba.dup === 0 && st.boards.cba.dup === 0, JSON.stringify(st.boards));

  // ── 2. 200 次随机交易：每笔之后即时验证不变量 ───────────
  const tr = JSON.parse(win.eval(`JSON.stringify((function(){
    let ops=0,fail='';
    for(let i=0;i<200;i++){
      const lg=R.chance(.5)?'nba':'cba';const b=S.pickBoard[lg];
      const cands=b.assets.filter(function(x){return x.owner===x.orig;});
      if(!cands.length){fail='no-candidates';break;}
      const a=R.pick(cands);
      const teams=TEAMS[lg].map(function(t){return t[0];}).filter(function(t){return t!==a.owner;});
      const to=R.pick(teams);
      if(!execPickTrade(lg,a.owner,to,a)){fail='exec-refused';break;}
      ops++;
      const seen={};
      for(const x of b.assets){
        const k=x.y+'|'+x.r+'|'+x.orig;
        if(seen[k]){fail='dup:'+k;break;}seen[k]=1;
        if(!TEAMS[lg].some(function(t){return t[0]===x.owner;})){fail='bad-owner:'+x.owner;break;}
      }
      if(fail)break;
    }
    return {ops,fail};})())`));
  check('200 次随机签位交易全部成交', tr.ops === 200, JSON.stringify(tr));
  check('每次交易后 I1/I2 都成立', !tr.fail, String(tr.fail));

  // ── 3. I3 冒名交易必须被拒 ──────────────────────────
  const imp = win.eval(`(function(){
    const a=S.pickBoard.nba.assets.find(function(x){return x.owner!==x.orig;})||S.pickBoard.nba.assets[0];
    const impostor=TEAMS.nba.map(function(t){return t[0];}).find(function(t){return t!==a.owner;});
    const before=a.owner;
    const refused=execPickTrade('nba',impostor,'任何队',a)===null;
    return {refused:refused,unchanged:a.owner===before};})()`);
  check('I3 非持有方发起交易被拒绝', imp.refused === true && imp.unchanged === true, JSON.stringify(imp));

  // ── 4. I4 保护条款：确定性场景 ───────────────────────
  const prot = JSON.parse(win.eval(`JSON.stringify((function(){
    S.pickBoard={};ensurePickBoard();          // 重置成干净板
    const year=curDraftYear();
    const order=draftOrderOf('nba').order;     // 战绩最差在前（含乐透扰动）
    const worst=order[0];const buyer=order[order.length-1];
    const a=pickAssetOf('nba',year,1,worst);a.owner=buyer;a.prot=3;
    const res=draftOwnership('nba',order,year);
    const top=res[0];
    const othersFine=res.slice(1).every(function(o){return o.owner===o.orig&&!o.reverted;});
    return {reverted:top.reverted,ownerIsOrig:top.owner===worst,comp:top.comp,
            othersFine:othersFine};})())`));
  check('I4 保护触发：槽位落入前 N 保护 → 归还原队', prot.reverted === true && prot.ownerIsOrig === true, JSON.stringify(prot));
  check('触发后受让方获得补偿（次轮签或现金）', (prot.comp || '').length > 0, String(prot.comp));
  check('其余槽位不受影响', prot.othersFine === true, JSON.stringify(prot));
  const noProt = JSON.parse(win.eval(`JSON.stringify((function(){
    S.pickBoard={};ensurePickBoard();
    const year=curDraftYear();
    const order=draftOrderOf('nba').order;
    const worst=order[0];const buyer=order[order.length-1];
    const a=pickAssetOf('nba',year,1,worst);a.owner=buyer;a.prot=null;   // 无保护
    const res=draftOwnership('nba',order,year);
    return {heldByBuyer:res[0].owner===buyer,reverted:res[0].reverted};})())`));
  check('I4 无保护签：持有方正常行使', noProt.heldByBuyer === true && noProt.reverted === false, JSON.stringify(noProt));

  // ── 5. 200 次随机归属解析：I4/I5 全程成立 ───────────────
  const ov = JSON.parse(win.eval(`JSON.stringify((function(){
    let fail='';
    for(let i=0;i<200;i++){
      S.pickBoard={};ensurePickBoard();
      const lg=R.chance(.5)?'nba':'cba';
      for(let k=0;k<20;k++){                       // 每轮先随机撒 20 笔交易
        const b=S.pickBoard[lg];const a=R.pick(b.assets);
        const to=R.pick(TEAMS[lg].map(function(t){return t[0];}).filter(function(t){return t!==a.owner;}));
        execPickTrade(lg,a.owner,to,a);
      }
      const order=draftOrderOf(lg).order;
      const res=draftOwnership(lg,order,curDraftYear());
      if(res.length!==order.length){fail='len';break;}
      for(const o of res){
        if(!TEAMS[lg].some(function(t){return t[0]===o.team;})){fail='slot-owner:'+o.team;break;}   // I5
        if(o.reverted&&o.owner!==o.orig){fail='revert-not-orig';break;}                              // I4a
        if(!o.reverted&&o.prot!=null&&o.owner!==o.orig&&o.slot-1<o.prot){fail='prot-ignored:'+o.slot;break;}  // I4b
      }
      if(fail)break;
    }
    return {fail};})())`));
  check('200 次随机归属解析全部满足 I4/I5', ov.fail === '', String(ov.fail));

  // ── 6. 截止日 AI 交易接入（新闻可见）────────────────────
  const news = JSON.parse(win.eval(`JSON.stringify((function(){
    S.worldNews=[];ensurePickBoard();
    const before={};['nba','cba'].forEach(function(lg){S.pickBoard[lg].assets.forEach(function(a){
      const k=lg+'|'+a.y+'|'+a.r+'|'+a.orig;before[k]=a.owner;});});
    const news=[];aiPickTrades(news);
    const moved=[];['nba','cba'].forEach(function(lg){S.pickBoard[lg].assets.forEach(function(a){
      const k=lg+'|'+a.y+'|'+a.r+'|'+a.orig;if(before[k]!==a.owner)moved.push(k);});});
    return {newsN:news.length,movedN:moved.length,agrees:news.length>=moved.length};})())`));
  check('截止日 AI 签位交易真实成交（资产板变动）', news.movedN >= 1, JSON.stringify(news));
  check('成交都有新闻播报（不多不少）', news.newsN === news.movedN, JSON.stringify(news));
});
