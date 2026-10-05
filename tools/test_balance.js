/* 难度重做（v4.20.0）——回归钉：
 *  ① 天赋上限下调（S ≤93 / A ≤82）与成长曲线放缓（收敛 ≤12% / 训练加成 ≤6 / 成年回落 ≥.76）
 *  ② NPC 顶星上限 92（联盟有真对手）
 *  ③ 继续征战真的续战：contN 计数、最多 3 次、45 岁开局强制退役 */
const { run } = require('./testkit');

module.exports = run('难度平衡', ({ win, check, html }) => {
  win.eval('renderCreate();');
  win.eval("document.getElementById('fName').value='难度测试';");
  win.eval('doCreate(); allocRandom(); confirmAlloc();');
  win.eval(`
    S.league='NBA'; S.team=TEAMS.nba[0][0]; S.age=30; ensureWorld();
  `);

  // ── ① 上限与成长曲线 ──
  const cfg = JSON.parse(win.eval(`JSON.stringify({
    tiers:TIER_RANGE, growth:GROWTH
  })`));
  check('S 档上限 ≤93（原 99）', cfg.tiers.S.max <= 93, String(cfg.tiers.S.max));
  check('A 档上限 ≤82（原 84）', cfg.tiers.A.max <= 82, String(cfg.tiers.A.max));
  check('成长收敛 ≤12%（原 16%）', cfg.growth.convUp <= 0.12, String(cfg.growth.convUp));
  check('训练加成上限 ≤6（原 8）', cfg.growth.grindMax <= 6, String(cfg.growth.grindMax));
  check('成年超限回落 ≤78%（原 82%）', cfg.growth.overKeep <= 0.78, String(cfg.growth.overKeep));

  // ── ② NPC 顶星上限 ──
  const npc = JSON.parse(win.eval(`JSON.stringify((function(){
    let mx=0,hi=0;
    for(let i=0;i<300;i++){const p=genPlayer('nba','测试队',7);mx=Math.max(mx,p.o);if(p.o>=88)hi++;}
    return {mx:mx,hi:hi};
  })())`));
  check('NPC 能力上限 = 92（原 88）', npc.mx <= 92, String(npc.mx));
  check('NPC 会出现 88+ 的顶星（联盟有真对手）', npc.hi > 0, String(npc.hi));

  // ── ③ 继续征战 —— 真的续战 + 硬上限 ──
  win.eval('S.flags.contN=0;');
  win.eval('applyFx({continued:1});');
  check('续战第 1 次计数为 1', win.eval('S.flags.contN') === 1, String(win.eval('S.flags.contN')));
  win.eval('applyFx({continued:1});applyFx({continued:1});');
  check('续战可累计到 3 次', win.eval('S.flags.contN') === 3, String(win.eval('S.flags.contN')));
  check('终章规则带续战上限（contN<3）', html.indexOf('(S.flags.contN||0)<3') >= 0);
  check('45 岁强制退役规则就位', html.indexOf('S.age>=45&&!S.retired') >= 0);

  // 行为：45 岁开局 → nextYear 直接进终章
  win.eval(`
    S.age=45; S.retired=false; S.flags.contN=3; S.stage='winter';
    UI={mode:'season'}; nextYear();
  `);
  const after = JSON.parse(win.eval(`JSON.stringify({retired:S.retired, mode:UI.mode})`));
  check('45 岁开局强制退役并进终章页', after.retired === true && after.mode === 'end', JSON.stringify(after));
});
