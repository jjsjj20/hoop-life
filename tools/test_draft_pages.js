/* NBA 选秀与签位抽签系统（v4.26.0）验收：
 * ① 休赛期序列：赛季页 →（NBA）签位抽签页 → 选秀大会页 → 下一年（抽签在前）
 * ② 抽签由常规赛战绩决定：乐透区 = 战绩最差 14 队、结果全部来自乐透区
 * ③ 年内幂等：同一届只生成一份签位表（两个页面/公告读同一份）
 * ④ 选秀 60 顺位全部落定；选中的球员写入球队名单（含玩家参选路径）
 * ⑤ 新秀首季保留 rk 参评标记（worldTick 清标不误伤刚选中的新秀）
 * ⑥ 非 NBA 球员的休赛期不出现这两个页面
 * ⑦ 班底名字构成：中国面孔稀少（约 4%，v4.26.1） */
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

  /* ── 抽签页渲染 ── */
  win.eval('renderGame();');
  const stage1 = doc.querySelector('#stage').textContent;
  check('抽签页：标题 / 球队 / 前往选秀按钮就位',
    stage1.includes('选秀抽签') && stage1.includes('前往选秀大会') && stage1.includes(snap.draw[0].team));

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

  /* 选秀页渲染 */
  win.eval('renderGame();');
  const stage2 = doc.querySelector('#stage').textContent;
  check('选秀页：标题 / 首轮 / 次轮 / 状元名字就位',
    stage2.includes('选秀大会') && stage2.includes('首轮（1-30）') && stage2.includes('次轮（31-60）') && stage2.includes(topPick.n));

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
});
