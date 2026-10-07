/* NBA 选秀与签位抽签系统（v4.26.0）验收：
 * ① 休赛期序列：赛季页 →（NBA）签位抽签页 → 选秀大会页 → 下一年（抽签在前）
 * ② 抽签由常规赛战绩决定：乐透区 = 战绩最差 14 队、结果全部来自乐透区
 * ③ 年内幂等：同一届只生成一份签位表（两个页面/公告读同一份）
 * ④ 选秀 60 顺位全部落定；选中的球员写入球队名单（含玩家参选路径）
 * ⑤ 新秀首季保留 rk 参评标记（worldTick 清标不误伤刚选中的新秀）
 * ⑥ 非 NBA 球员的休赛期不出现这两个页面
 * ⑦ 班底组成：中国面孔稀少（约 4%）· 按顺位加权 · 整体降格（v4.26.1 / v4.27.1）
 * ⑧ 玩家参选仪式（v4.27.0）：选秀夜 → 抽签揭牌 → 逐位念到本人（或念完落选）→ 结果页 */
const { run } = require('./testkit');

module.exports = run('选秀与抽签页面', ({ win, doc, check }) => {
  win.eval('renderCreate();');
  doc.querySelector('#fName').value = '选秀测试';
  win.eval('doCreate(); allocRandom(); confirmAlloc();');
  win.eval("S.league='NBA'; S.team=TEAMS.nba[10][0]; S.teamStr=TEAMS.nba[10][1]; S.age=25; S.stage='playoffs'; S.starter=true; ensureWorld(); S._stCache={};");

  const nbaTeams = win.eval('TEAMS.nba.map(t=>t[0])');
  const ageBefore = win.eval('S.age');

  /* ── ① 顺序：赛季页按钮先到抽签页（不是直接下一年） ── */
  win.eval('seasonNext();');
  const m1 = win.eval('UI.mode');
  check('赛季页「进入下一年」先进入签位抽签页', m1 === 'lottery', String(m1));
  check('抽签页出现时还没有进下一年（age 未变）', win.eval('S.age') === ageBefore, String(win.eval('S.age')));

  /* ── ② 抽签由常规赛战绩决定 ── */
  const snap = JSON.parse(win.eval(`JSON.stringify((function(){
    const w={};computeStandings('nba').forEach(r=>{w[r.team]=r.wins;});
    const plan=draftPlanFor(curDraftYear());
    return {wins:w,order:plan.order,lotto:plan.lotto,draw:plan.draw,recs:Object.keys(plan.recs).length};
  })())`));
  const wOf = t => snap.wins[t];
  const isAsc = a => a.every((v, i) => i === 0 || a[i - 1] <= v);
  check('签位表 = 30 队排列 · 乐透 14 队只抽 4 签',
    snap.order.length === 30 && new Set(snap.order).size === 30 && snap.lotto.length === 14 && snap.draw.length === 4);
  const lotW = snap.lotto.map(wOf), othW = snap.order.filter(t => !snap.lotto.includes(t)).map(wOf);
  check('乐透区 = 战绩最差的 14 队', Math.max(...lotW) <= Math.min(...othW),
    `乐透最差 ${Math.max(...lotW)} vs 非乐透最好 ${Math.min(...othW)}`);
  check('前 4 签全部来自乐透区', snap.draw.every(d => snap.lotto.includes(d.team)));
  check('5-14 签为剩余乐透队 · 战绩倒序', isAsc(snap.order.slice(4, 14).map(wOf)));
  check('页面战绩快照覆盖 30 队（与抽签同源）', snap.recs === 30, String(snap.recs));

  /* ── ③ 年内幂等：再取还是同一份 ── */
  const samePlan = win.eval(`(function(){const a=draftPlanFor(curDraftYear()),b=draftPlanFor(curDraftYear());
    return a===b&&JSON.stringify(a.order)===JSON.stringify(b.order)&&JSON.stringify(a.draw)===JSON.stringify(b.draw);})()`);
  check('同一届签位表只生成一份（两次取到同一对象）', samePlan === true);

  /* ── 抽签页渲染：逐位揭牌（v4.26.2） ── */
  win.eval('renderGame();');
  let st = doc.querySelector('#stage').textContent;
  const hitCount = () => (doc.querySelector('#stage').textContent.match(/概率命中/g) || []).length;
  check('抽签页初始：四签全部「？？？」，按钮=揭晓状元签',
    st.includes('选秀抽签') && (st.match(/？？？/g) || []).length === 4 && st.includes('揭晓状元签') && hitCount() === 0);
  win.eval('revealLottery();');
  check('揭牌一次：状元签出现、按钮切到榜眼签',
    hitCount() === 1 && doc.querySelector('#stage').textContent.includes('揭晓榜眼签'));
  check('揭晓进度写入 UI（存档可续）', win.eval('UI.lr') === 1, String(win.eval('UI.lr')));
  win.eval('revealLottery();revealLottery();revealLottery();');
  st = doc.querySelector('#stage').textContent;
  check('四签揭完：出现「前往选秀大会」+ 最终顺位标注',
    hitCount() === 4 && st.includes('前往选秀大会') && st.includes('第14顺位'));

  /* ── ④ 选秀大会：60 顺位全部落定并写入名单 ── */
  const worldBefore = win.eval('S.world.nba.length');
  win.eval('goDraftDay();');
  const m2 = win.eval('UI.mode');
  check('抽签页之后是选秀大会页（顺序正确）', m2 === 'draftday', String(m2));
  const plan2 = JSON.parse(win.eval('JSON.stringify(draftPlanFor(curDraftYear()))'));
  check('本届 60 签全部落定', plan2.picks.length === 60 && plan2.resolved === true);
  check('每签都有合法球队与球员', plan2.picks.every(p => nbaTeams.includes(p.team) && !!p.n && !!p.p));
  const worldAfter = win.eval('S.world.nba.length');
  check('60 名新秀全部写入名单', worldAfter - worldBefore === 60, `${worldBefore} → ${worldAfter}`);
  const topPick = plan2.picks[0];
  const inRoster = win.eval(`(function(){const p=draftPlanFor(curDraftYear()).picks[0];
    return S.world.nba.some(w=>w.t===p.team&&w.n===p.n&&w.pot!=null&&w.a>=19&&w.a<=23&&w.pend===1);})()`);
  check('状元签选中的人出现在该队名单（带潜力/年龄/入行标记）', inRoster === true);

  /* 选秀页渲染：逐位宣布（v4.26.2） */
  st = doc.querySelector('#stage').textContent;
  check('选秀页初始：0/60，尚未公布任何名字',
    st.includes('选秀大会') && st.includes('已公布 0 / 60') && st.includes('宣布第 1 顺位'));
  check('初始状态不泄露顺位结果', !st.includes('#1 ') && !st.includes(topPick.n));
  win.eval('revealPick();');
  st = doc.querySelector('#stage').textContent;
  check('宣布一次 → 状元（#1）出现、进度 1/60',
    st.includes('已公布 1 / 60') && st.includes('#1 ') && st.includes(topPick.n) && st.includes('宣布第 2 顺位'));
  win.eval('revealAllPicks();');
  st = doc.querySelector('#stage').textContent;
  check('直接看完全部 → 首轮/次轮全表 + 进入下一年',
    st.includes('首轮（1-30）') && st.includes('次轮（31-60）') && st.includes('进入下一年') && st.includes(plan2.picks[59].n));

  /* ── ⑤ 新秀标记：进入下一年后 rk 保留 ── */
  win.eval('nextYear();');
  check('休赛期结束进入下一年', win.eval('S.age') === ageBefore + 1, String(win.eval('S.age')));
  const rkKept = win.eval(`(function(){
    return S.world.nba.some(w=>w.n===${JSON.stringify(topPick.n)}&&w.t===${JSON.stringify(topPick.team)}&&w.rk===1&&!w.pend);})()`);
  check('刚选中的新秀首季保留参评标记（rk=1，pend 已清）', rkKept === true);

  /* ── 玩家参选路径：resolveDraftInto 把玩家插进顺位、其余照常落位 ── */
  const meCheck = win.eval(`(function(){
    const order=draftPlanFor(curDraftYear()).order;
    const n0=S.world.nba.length;
    const r=resolveDraftInto(order,23,{name:'测试员',pos:'PG',ovr:72,age:19});
    return {len:r.picks.length, at:r.picks[22]?r.picks[22].me:null, nm:r.picks[22]?r.picks[22].n:null,
      added:S.world.nba.length-n0, hasMe:r.picks.some(p=>p.me)};
  })()`);
  check('玩家参选：第 23 位插入玩家本人', meCheck.at === true && meCheck.nm === '测试员');
  check('玩家参选：其余 59 签照常落位入队', meCheck.len === 60 && meCheck.added === 59);

  /* ── ⑥ 非 NBA：跳过页面直接进下一年 ── */
  win.eval("S.league='CBA'; S.stage='playoffs';");
  const a2 = win.eval('S.age');
  win.eval('seasonNext();');
  check('非 NBA 职业：不出现选秀页面，直接进下一年',
    win.eval('S.age') === a2 + 1 && win.eval('UI.mode') !== 'lottery' && win.eval('UI.mode') !== 'draftday');

  /* ── ⑦ 班底名字构成：中国面孔稀少（v4.26.1；300 抽样期望 12，上界 30） ── */
  const cnCnt = win.eval(`(function(){let c=0;for(let i=0;i<300;i++){if(/[\\u4e00-\\u9fa5]/.test(draftProspect().n))c++;}return c;})()`);
  check('中国球员存在但稀少（1~30 / 300，约 4%）', cnCnt >= 1 && cnCnt <= 30, String(cnCnt));

  /* ── ⑦b 班底按顺位加权 + 整体降格（v4.27.1 膨胀平衡修复） ── */
  const curve = JSON.parse(win.eval(`JSON.stringify((function(){
    let a=0,b=0;for(let k=0;k<200;k++){a+=draftProspect(3).o;b+=draftProspect(55).o;}
    return {a:Math.round(a/200*10)/10,b:Math.round(b/200*10)/10};
  })())`));
  check('班底按顺位加权（探花期望 − 55 号期望 ≥ 15）', curve.a - curve.b >= 15, `探花 ${curve.a} vs 55号 ${curve.b}`);
  const classAvgO = win.eval(`(function(){let s=0,n=0;for(let r=0;r<10;r++)for(let pk=1;pk<=60;pk++){s+=draftProspect(pk).o;n++;}return Math.round(s/n*10)/10;})()`);
  check('班底整体降格（全届平均能力 48~62）', classAvgO >= 48 && classAvgO <= 62, String(classAvgO));

  /* ── ⑧ 玩家参选仪式：场景一「落选」（stock=72 → 顺位必 >60） ── */
  const nightScene = win.eval(`
    S.age=20; S.league='CBA'; S.stage='summer'; S.retired=false;
    S.team='广东华南虎'; S.teamStr=8; S.flags.undrafted=false;
    S.draftPlans={};
    const _d1=newDraft(); _d1.stock=72; S.draft=_d1;
    evDraftNight().scene;
  `);
  check('选秀夜夜景不再提前剧透抽签', String(nightScene).indexOf('乐透抽签') < 0);
  const worldPre1 = win.eval('S.world.nba.length');
  win.eval('UI={mode:"event",ev:evDraftNight()};choose(0);');
  check('落选场景：选秀夜 → 先进入抽签揭晓页（crm 随行）',
    win.eval('UI.mode') === 'lottery' && win.eval('!!(UI.crm&&UI.crm.ev&&UI.crm.ev.id)') === true);
  check('落选场景：确为落选（stock 72 被 cap 至 61+）', win.eval('S.flags.undrafted') === true);
  win.eval('revealLottery();revealLottery();revealLottery();revealLottery();goDraftDay();');
  check('仪式：抽签页走完 → 选秀大会页（crm 随行）',
    win.eval('UI.mode') === 'draftday' && win.eval('!!UI.crm') === true);
  check('落选场景：计划里没有 me 顺位', win.eval('draftPlanFor(curDraftYear()).picks.filter(p=>p.me).length') === 0);
  win.eval('revealAllPicks();');
  const cx1 = doc.querySelector('#stage').textContent;
  check('落选场景：60 位念完出现「没有念到他」+ 继续', cx1.includes('没有念到他') && cx1.includes('继续 ▶'));
  win.eval('finishDraftCeremony();');
  check('落选场景：回到结果页（含落选播报）',
    win.eval('UI.mode') === 'result' && win.eval('UI.ev.id') === 'draftNight' &&
    win.eval('UI.changes.join("|")').indexOf('没有被念到') >= 0);
  check('落选场景：60 名 NPC 新秀照常入队', win.eval('S.world.nba.length') - worldPre1 === 60,
    String(win.eval('S.world.nba.length') - worldPre1));

  /* ── ⑨ 玩家参选仪式：场景二「被念到名字」（stock=8 → 顺位 3~16） ── */
  const worldPre2 = win.eval('S.world.nba.length');
  win.eval(`
    S.age=21; S.league='CBA'; S.stage='summer';
    S.team='广东华南虎'; S.teamStr=8; S.flags.undrafted=false;
    S.draftPlans={}; S.draft=null;
    const _d2=newDraft(); _d2.stock=8; S.draft=_d2;
    UI={mode:'event',ev:evDraftNight()};
    choose(0);
  `);
  check('选秀场景：进入抽签揭晓页', win.eval('UI.mode') === 'lottery');
  win.eval('revealLottery();revealLottery();revealLottery();revealLottery();goDraftDay();');
  const meP = JSON.parse(win.eval('JSON.stringify(draftPlanFor(curDraftYear()).picks.filter(p=>p.me)[0]||null)'));
  check('计划里插入玩家本人（me 标记 · 顺位 3~16）',
    !!meP && meP.n === '选秀测试' && meP.pick >= 3 && meP.pick <= 16,
    JSON.stringify(meP && { pick: meP.pick, team: meP.team }));
  check('防剧透：念到之前对外仍显示原球队（顶栏/侧栏/阵容同源）',
    win.eval('myTeamName()') === '广东华南虎' && win.eval('teamLabel()').indexOf('广东华南虎') >= 0,
    String(win.eval('teamLabel()')));
  win.eval(`for(let k=0;k<${meP.pick};k++)revealPick();`);
  check('逐位念到自己即定格', win.eval('UI.dr') === meP.pick, String(win.eval('UI.dr')));
  check('揭晓后对外恢复新球队', win.eval('myTeamName()') === meP.team, String(win.eval('myTeamName()')));
  const cx2 = doc.querySelector('#stage').textContent;
  check('定格画面：「选择了你」+ 继续按钮', cx2.includes('选择了你') && cx2.includes('继续 ▶'));
  win.eval('revealPick();');
  check('到达本人顺位后不再越过（封顶）', win.eval('UI.dr') === meP.pick);
  win.eval('finishDraftCeremony();');
  check('仪式收尾清掉防剧透暂存', win.eval('!S._preDraft') === true);
  check('被选中结果页回归（第 N 顺位播报 · 无重复乐透播报）',
    win.eval('UI.mode') === 'result' &&
    win.eval('UI.changes.join("|")').indexOf('选择了 选秀测试') >= 0 &&
    win.eval('UI.changes.join("|")').indexOf('乐透抽签') < 0);
  check('选秀场景：其余 59 签入队（玩家不在 NPC 名单里）', win.eval('S.world.nba.length') - worldPre2 === 59,
    String(win.eval('S.world.nba.length') - worldPre2));
});
