/* 赛季推进（nextYear）—— 改动最危险、此前零覆盖的路径
 *
 * 为什么值得测：nextYear() 一季要动十几处状态（年龄/阶段/伤病顺延/训练营到期/
 * 世界推进/榜单接续/退役衔接），任何一处写错都不会报错，只会让生涯悄悄走偏。
 * 这里不追求覆盖每个分支，而是钉死一批**跨赛季必须成立的不变量**。
 */
const { run } = require('./testkit');

module.exports = run('赛季推进', ({ win, doc, check }) => {
  win.eval('renderCreate();');
  doc.querySelector('#fName').value = '测试';
  win.eval('doCreate(); allocRandom(); confirmAlloc();');
  // 造一个在 NBA 打了几年、世界已生成的职业档——这才是 nextYear 的真实负载
  win.eval(`
    S.league='NBA';S.team='洛杉矶湖人';S.teamStr=8;S.age=26;S.role='player';S.ts=5;
    ensureWorld(); if(!S.contract)setContract(S.team,'NBA',3,'职业合同');
    S.stage='spring';S.stageDone=0;S.stageNeed=stageNeedFor();
    S.career.seasons=3;S.career.pts=3600;S.career.reb=900;S.career.ast=700;
    S.honors=[{y:'2026-27赛季',t:'全明星'}];
    S.form=80;S.focus={x:1};S.injuryMissed=5;S.camp={n:'特训',perm:{durability:2}};
    S.standings={lg:'nba',season:seasonLabel(),rows:computeStandings('nba')};
    S.log=[{y:'2026-27赛季',t:'测试日志'}];
  `);
  const worldBefore = win.eval('(function(){let n=0;for(const k in S.world)n+=S.world[k].length;return n;})()');
  check('前置：球员世界已生成', worldBefore > 500, worldBefore + ' 人');

  // ── 连推 10 个赛季 ─────────────────────────────────
  const trace = [];
  let threw = null;
  try {
    for (let i = 1; i <= 10; i++) {
      const before = JSON.parse(win.eval('JSON.stringify({age:S.age,honors:S.honors.length,log:S.log.length})'));
      win.eval('nextYear();');
      const after = JSON.parse(win.eval(`JSON.stringify({
        age:S.age, stage:S.stage, done:S.stageDone, focus:S.focus,
        missed:S.injuryMissed, camp:S.camp, honors:S.honors.length, log:S.log.length,
        world:(function(){let n=0;for(const k in S.world)n+=S.world[k].length;return n;})(),
        stageNeed:S.stageNeed, league:S.league, retired:!!S.retired
      })`));
      trace.push(after);
      check(`第 ${i} 季：年龄 +1`, after.age === before.age + 1, before.age + '→' + after.age);
      check(`第 ${i} 季：阶段重置为 spring 且进度归零`, after.stage === 'spring' && after.done === 0,
        after.stage + '/' + after.done);
      check(`第 ${i} 季：焦点战清空、缺阵场次归零、训练营到期`,
        after.focus === null && after.missed === 0 && after.camp === null,
        JSON.stringify({ focus: after.focus, missed: after.missed, camp: after.camp }));
      check(`第 ${i} 季：荣誉与日志只增不减`, after.honors >= before.honors && after.log >= before.log,
        'honors ' + before.honors + '→' + after.honors + ' / log ' + before.log + '→' + after.log);
      check(`第 ${i} 季：球员世界仍完整`, after.world > 500, after.world + ' 人');
      check(`第 ${i} 季：阶段配额有效`, after.stageNeed >= 1, String(after.stageNeed));
    }
  } catch (e) { threw = e; }
  check('连推 10 季不抛异常', !threw, threw && (threw.message + ' @ ' + (threw.stack || '').split('\n')[1]));

  check('10 季后年龄正确递增', trace.length === 10 && trace[9].age === 36, trace.length ? String(trace[9].age) : 'n/a');

  // ── 跨赛季存档往返：状态不能丢 ───────────────────────
  const snap = JSON.parse(win.eval(`JSON.stringify({
    age:S.age, seasons:S.career.seasons, pts:S.career.pts, honors:S.honors.length,
    world:(function(){let n=0;for(const k in S.world)n+=S.world[k].length;return n;})(),
    team:S.team, league:S.league, pos:S.pos, name:S.name
  })`));
  const j = win.eval('saveJson()');
  check('存档可序列化且非空', typeof j === 'string' && j.length > 20000, String(j && j.length));
  win.eval('S=null;UI=null;');
  win.eval(`(function(){
    const d=JSON.parse(localStorage.getItem(CFG.SAVE_KEY));S=d.S;ensureState();ensureWorld();fixRosterAll();
  })()`);
  const back = JSON.parse(win.eval(`JSON.stringify({
    age:S.age, seasons:S.career.seasons, pts:S.career.pts, honors:S.honors.length,
    world:(function(){let n=0;for(const k in S.world)n+=S.world[k].length;return n;})(),
    team:S.team, league:S.league, pos:S.pos, name:S.name
  })`));
  Object.keys(snap).forEach(k => {
    if (k === 'world') {
      check('读档后球员世界规模一致', Math.abs(back.world - snap.world) <= 2, snap.world + ' → ' + back.world);
    } else {
      check('读档后 ' + k + ' 保持一致', back[k] === snap[k], JSON.stringify(snap[k]) + ' → ' + JSON.stringify(back[k]));
    }
  });

  // ── 年龄上限：不能无限推进 ────────────────────────────
  win.eval('S.age=41;');
  let ceiling = null;
  try { win.eval('nextYear();'); } catch (e) { ceiling = e; }
  check('41 岁推进不崩', !ceiling, ceiling && ceiling.message);
  check('推进后年龄仍在合理区间', win.eval('S.age') <= 45, String(win.eval('S.age')));
});
