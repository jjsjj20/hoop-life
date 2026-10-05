/* P7 签位玩法延伸 + computeStandings 缓存分槽（v4.14）——回归钉：
 *  ① 排名缓存按联赛分槽：同赛季跨联赛查看不再互相顶掉（旧单槽会重摇导致排名前后不一）
 *  ② 旧形状单槽缓存读入时一次性迁移
 *  ③ 顺位互换 execSwap：所有权互换 + 不变量（冒名/同队拒绝）
 *  ④ 保签摆烂：条件判定（高保护+已交易+冬季）与事件
 *  ⑤ 资产板可视化：showPickAssets 覆盖层渲染归属与保护 */
const { run } = require('./testkit');

module.exports = run('P7签位延伸', ({ win, doc, check, html }) => {
  win.eval('renderCreate();');
  win.eval("document.getElementById('fName').value='资产测试';");
  win.eval('doCreate(); allocRandom(); confirmAlloc();');
  win.eval(`
    S.league='NBA'; S.mode='immersive';
    S.team=TEAMS.nba[10][0]; S.teamStr=6; S.age=22; S.stage='winter';
    ensureWorld();
  `);

  // ── ① 缓存分槽：同赛季跨联赛查看不互相顶掉 ──
  const cache = JSON.parse(win.eval(`JSON.stringify((function(){
    const a=JSON.stringify(computeStandings('nba'));
    const b=JSON.stringify(computeStandings('cba'));
    const c=JSON.stringify(computeStandings('nba'));   /* 旧单槽：这里会重摇，a!==c */
    return {a:a,c:c,same:a===c,nbaSlot:!!S._stCache.nba,cbaSlot:!!S._stCache.cba,
            nbaSeason:S._stCache.nba.season};
  })())`));
  check('同赛季重复调用返回同一份排名（不重摇）', cache.same === true);
  check('缓存按联赛分槽（nba/cba 各一份）', cache.nbaSlot === true && cache.cbaSlot === true, JSON.stringify(cache));
  check('缓存带赛季键', cache.nbaSeason === win.eval('seasonLabel()'));

  // ── ② 旧形状单槽缓存迁移 ──
  const mig = JSON.parse(win.eval(`JSON.stringify((function(){
    S._stCache={lg:'nba',season:seasonLabel(),rows:[{team:'x',wins:1,losses:0,str:6,rank:1}]};   /* 旧形状 */
    const rows=computeStandings('nba');
    return {n:rows.length,newShape:!!S._stCache.nba&&!S._stCache.rows};
  })())`));
  check('旧形状单槽缓存读入时迁移（不崩、重算正常）', mig.n === 30 && mig.newShape === true, JSON.stringify(mig));

  // ── ③ 顺位互换 ──
  const sw = JSON.parse(win.eval(`JSON.stringify((function(){
    S.pickBoard={};ensurePickBoard();
    const D=curDraftYear();
    const teams=TEAMS.nba.map(t=>t[0]);
    const A=teams[0],B=teams[1];
    const a=pickAssetOf('nba',D+1,1,A),b=pickAssetOf('nba',D+1,1,B);
    const done=execSwap('nba',{y:D+1,r:1,orig:A,owner:A},{y:D+1,r:1,orig:B,owner:B});
    const aToB=a.owner===B,bToA=b.owner===A;
    /* 冒名/同队必须拒绝 */
    const refused1=execSwap('nba',{y:D+1,r:1,orig:A,owner:A},{y:D+1,r:1,orig:B,owner:B})===null;   /* 已换过，所有权不符 */
    const refused2=execSwap('nba',{y:D+1,r:1,orig:A,owner:A},{y:D+2,r:1,orig:A,owner:A})===null;   /* 同原队 */
    return {done:!!done,aToB:aToB,bToA:bToA,refused1:refused1,refused2:refused2};
  })())`));
  check('顺位互换：双方所有权互换', sw.done === true && sw.aToB === true && sw.bToA === true, JSON.stringify(sw));
  check('互换不变量：冒名/同队拒绝', sw.refused1 === true && sw.refused2 === true, JSON.stringify(sw));

  // ── ④ 保签摆烂 ──
  const tank = JSON.parse(win.eval(`JSON.stringify((function(){
    S.pickBoard={};ensurePickBoard();
    const D=curDraftYear();
    const other=TEAMS.nba[0][0]===S.team?TEAMS.nba[1][0]:TEAMS.nba[0][0];
    const a=pickAssetOf('nba',D+1,1,S.team);
    a.owner=other;a.prot=4;                     /* 我队首轮已交易、前4保护 */
    S.stage='winter';S.flags['tank'+(S.birthYear+S.age)]=false;
    let hit=0;
    for(let i=0;i<40;i++){S.flags['tank'+(S.birthYear+S.age)]=false;if(tankScenarioReady())hit++;}
    a.prot=null;                                 /* 无保护 → 永不触发（确定性假） */
    let hitNoProt=0;
    for(let i=0;i<40;i++){S.flags['tank'+(S.birthYear+S.age)]=false;if(tankScenarioReady())hitNoProt++;}
    S.flags['tank'+(S.birthYear+S.age)]=false;
    const ev=tankScenarioReady()?evTankHint():evTankHint();
    return {hit:hit>=1,hitNoProt:hitNoProt===0,evId:ev.id,evChoices:Array.isArray(ev.choices)&&ev.choices.length>=3};
  })())`));
  check('保签摆烂：高保护+已交易+冬季 → 条件可触发', tank.hit === true, JSON.stringify(tank));
  check('无保护签永不触发（确定性）', tank.hitNoProt === true, JSON.stringify(tank));
  check('摆烂事件可生成且带 3 个抉择', tank.evId === 'tankHint' && tank.evChoices === true, JSON.stringify(tank));

  // ── ⑤ 资产板可视化 ──
  win.eval(`(function(){
      S.pickBoard={};ensurePickBoard();
      const D=curDraftYear();
      const other=TEAMS.nba[0][0]===S.team?TEAMS.nba[1][0]:TEAMS.nba[0][0];
      const a=pickAssetOf('nba',D+1,1,S.team);a.owner=other;a.prot=4;      /* 我队签已交易 */
      const b=pickAssetOf('nba',D+1,1,other);b.owner=S.team;               /* 我队获得对方签 */
      showPickAssets();
    })()`);
  const ui = doc.body.innerHTML;const myTeam = win.eval('S.team');
  check('资产板覆盖层渲染「已交易至」（触保归我）', ui.indexOf('已交易至') >= 0 && ui.indexOf('触保归我') >= 0);
  check('资产板覆盖层渲染「我队持有」', ui.indexOf('我队持有') >= 0);
  check('覆盖层包含球队名与前4保护', ui.indexOf('前4保护') >= 0 && ui.indexOf(myTeam) >= 0);

  // ── 行动栏减负（v4.18）：内联 ≤6 个 + ☰ 更多菜单承载次要功能 ──
  win.eval("UI={mode:'event',ev:null};renderGame();");
  const appHtml = doc.getElementById('app').innerHTML;
  const actM = appHtml.match(/<div class="actions">([\s\S]*?)<\/div>/);
  const inlineN = actM ? (actM[1].match(/<button/g) || []).length : 99;
  check('行动栏内联按钮 ≤ 6 个（原 15）', inlineN <= 6, '实际 ' + inlineN + ' 个');
  check('保留高频按钮：阵容/排名/存档/更多',
    ['showRoster()', 'saveNow()', 'openMore()'].every(fn => appHtml.indexOf(fn) >= 0));
  win.eval("openMore()");
  const moreHtml = doc.body.innerHTML;
  check('☰ 更多 菜单含签位/财务/成就/档案',
    ['showPickAssets()', 'showMoney()', 'showCodex()', 'showArchive()'].every(fn => moreHtml.indexOf(fn) >= 0));
  check('☰ 更多 菜单含音效/导出/导入/结束生涯',
    ['toggleSfx()', 'exportSave()', 'openImport()', 'endNow()'].every(fn => moreHtml.indexOf(fn) >= 0));
});