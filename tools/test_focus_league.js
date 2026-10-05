/* 焦点战「联赛校验」回归钉（v3.2 修复，补录于 v4.x 基线）——
 *  ·  ① 老东家战（ex）：非本联赛的旧队（青训学院 / 大学校队）不得被排进 NBA 赛程
 *  ·  ② 复仇战（revenge）：淘汰者必须仍在本联赛；跨联赛残留（CBA 被淘汰→现打 NBA）应被拦截
 *  ·  ③ 奇数赛季复仇槽：条件不满足时退回「背靠背硬仗」（grind），冬段仍是 6 场不缺口
 *  ·  ④ focusOpponent：ex/revenge 返回的对手必须 ∈ 当前联赛球队名单 */
const { run } = require('./testkit');

module.exports = run('焦点战联赛校验', ({ win, doc, check }) => {
  win.eval('renderCreate();');
  win.eval("document.getElementById('fName').value='联赛校验';");
  win.eval('doCreate(); allocRandom(); confirmAlloc();');
  win.eval(`
    S.league='NBA'; S.mode='immersive';
    S.team=TEAMS.nba[5][0]; S.teamStr=6; S.age=25; S.stage='winter';
    ensureWorld();
  `);

  const nbaSet = win.eval("JSON.stringify(TEAMS.nba.map(t=>t[0]))");
  const nba = JSON.parse(nbaSet);
  const notNba = t => nba.indexOf(t) < 0;

  // ── ① 老东家战：履历里只有跨联赛旧队（IMG 学院 / UCLA）时不可约 ──
  const ex1 = JSON.parse(win.eval(`JSON.stringify((function(){
    S.played=['美国IMG学院','UCLA',S.team];   /* 全是非 NBA 旧队 */
    S.lastLossTeam=null;
    return {playable:focusPlayable('ex')};
  })())`));
  check('老东家全是跨联赛旧队 → ex 不可约（拦截 IMG/UCLA）', ex1.playable === false, JSON.stringify(ex1));

  const ex2 = JSON.parse(win.eval(`JSON.stringify((function(){
    S.played=[S.team,TEAMS.nba[20][0]];   /* 含一支 NBA 老东家 */
    return {playable:focusPlayable('ex'), old:TEAMS.nba[20][0]};
  })())`));
  check('老东家里有本联赛球队 → ex 可约', ex2.playable === true, JSON.stringify(ex2));

  // ── ② 复仇战：淘汰者必须仍在本联赛 ──
  const rvX = JSON.parse(win.eval(`JSON.stringify((function(){
    S.lastLossTeam='辽宁本钢';   /* 跨联赛（CBA）淘汰者 */
    return {playable:focusPlayable('revenge')};
  })())`));
  check('淘汰者在别的联赛（CBA）→ revenge 不可约', rvX.playable === false, JSON.stringify(rvX));

  const rvOk = JSON.parse(win.eval(`JSON.stringify((function(){
    S.lastLossTeam=TEAMS.nba[8][0];   /* 本联赛淘汰者 */
    return {playable:focusPlayable('revenge'), team:TEAMS.nba[8][0]};
  })())`));
  check('淘汰者在本联赛 → revenge 可约', rvOk.playable === true, JSON.stringify(rvOk));

  const rvSelf = JSON.parse(win.eval(`JSON.stringify((function(){
    S.lastLossTeam=S.team;   /* 自己淘汰自己（异常态）应拒绝 */
    return {playable:focusPlayable('revenge')};
  })())`));
  check('淘汰者=自己 → revenge 拒绝（异常态防护）', rvSelf.playable === false, JSON.stringify(rvSelf));

  // ── ③ 奇数赛季复仇槽：不满足 → 退回「背靠背硬仗」 ──
  const slotsBad = JSON.parse(win.eval(`JSON.stringify((function(){
    S.lastLossTeam=null; S.birthYear=2000; S.age=25;   /* 2000+25=2025 奇数 */
    const s=focusSlots('winter');
    return {slots:s, n:s.length, hasRevenge:s.indexOf('revenge')>=0, hasGrind:s.indexOf('grind')>=0};
  })())`));
  check('奇数赛季但无合格淘汰者 → 复仇槽退回背靠背硬仗', slotsBad.hasRevenge === false && slotsBad.hasGrind === true, JSON.stringify(slotsBad));
  check('冬段槽位仍是 6 场（不缺口）', slotsBad.n === 6, String(slotsBad.n));

  const slotsOk = JSON.parse(win.eval(`JSON.stringify((function(){
    S.lastLossTeam=TEAMS.nba[8][0];
    const s=focusSlots('winter');
    return {hasRevenge:s.indexOf('revenge')>=0, hasGrind:s.indexOf('grind')>=0};
  })())`));
  check('奇数赛季且有合格淘汰者 → 换上复仇战', slotsOk.hasRevenge === true && slotsOk.hasGrind === false, JSON.stringify(slotsOk));

  const slotsEven = JSON.parse(win.eval(`JSON.stringify((function(){
    S.lastLossTeam=TEAMS.nba[8][0]; S.age=24;   /* 2000+24=2024 偶数 */
    const s=focusSlots('winter');
    return {hasRevenge:s.indexOf('revenge')>=0, hasGrind:s.indexOf('grind')>=0};
  })())`));
  check('偶数赛季 → 固定用背靠背硬仗（不换复仇战）', slotsEven.hasRevenge === false && slotsEven.hasGrind === true, JSON.stringify(slotsEven));

  // ── ④ focusOpponent：返回的对手必须 ∈ 当前联赛 ──
  const oppEx = JSON.parse(win.eval(`JSON.stringify((function(){
    S.played=['美国IMG学院','UCLA',TEAMS.nba[20][0]];   /* 含跨联赛旧队 + 一支 NBA 旧队 */
    const o=focusOpponent('ex');
    return {team:o.team, inLg:TEAMS.nba.some(t=>t[0]===o.team)};
  })())`));
  check('focusOpponent(ex) 只挑本联赛老东家（不会挑到 IMG/UCLA）', oppEx.inLg === true && oppEx.team === win.eval('TEAMS.nba[20][0]'), JSON.stringify(oppEx));

  const oppRv = JSON.parse(win.eval(`JSON.stringify((function(){
    S.lastLossTeam='辽宁本钢';   /* 跨联赛 → 应被忽略，退回联赛内随机 */
    const o=focusOpponent('revenge');
    return {team:o.team, inLg:TEAMS.nba.some(t=>t[0]===o.team)};
  })())`));
  check('focusOpponent(revenge) 忽略跨联赛淘汰者、退回本联赛对手', oppRv.inLg === true && oppRv.team !== '辽宁本钢', JSON.stringify(oppRv));

  const oppRv2 = JSON.parse(win.eval(`JSON.stringify((function(){
    S.lastLossTeam=TEAMS.nba[8][0];
    const o=focusOpponent('revenge');
    return {team:o.team, want:TEAMS.nba[8][0]};
  })())`));
  check('focusOpponent(revenge) 本联赛淘汰者 → 精确约战该队', oppRv2.team === oppRv2.want, JSON.stringify(oppRv2));

  const oppExOnlyForeign = JSON.parse(win.eval(`JSON.stringify((function(){
    S.played=['美国IMG学院','UCLA',S.team];   /* 无本联赛旧队 */
    const o=focusOpponent('ex');
    return {team:o.team, inLg:TEAMS.nba.some(t=>t[0]===o.team), notNba:['美国IMG学院','UCLA'].indexOf(o.team)<0};
  })())`));
  check('focusOpponent(ex) 无本联赛老东家时退回本联赛对手（绝不回退到 IMG/UCLA）', oppExOnlyForeign.inLg === true && oppExOnlyForeign.notNba === true, JSON.stringify(oppExOnlyForeign));
});
