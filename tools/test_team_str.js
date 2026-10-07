/* 球队实力模型——前10人取样 + 权重 70/30 验收（v4.24.0）：
 * ① rosterStr 取前 10 人平均（第 11 人之后不影响结果）
 * ② teamStrength 权重 = 底子 30% + 阵容 70%（用 base 断点值验证）
 * ③ 阵容人数不足 5 人退回纯底子（旧行为保留）
 * ④ 产物字符串断言（新公式就位、旧公式移除、面板文案同口径） */
const { run } = require('./testkit');

module.exports = run('球队实力模型', ({ win, check, html }) => {
  win.eval('renderCreate();');
  win.eval("document.getElementById('fName').value='实力测试';");
  win.eval('doCreate(); allocRandom(); confirmAlloc();');
  win.eval("S.league='NBA'; ensureWorld();");

  const near = (a, b, eps) => Math.abs(a - b) < (eps || 1e-9);

  /* 注入合成阵容：顶 10 人均值 71 → rosterStr = 6.4+(71−74)×.75 = 4.15 */
  win.eval(`
    (function(){
      S.world.nba=S.world.nba.filter(p=>p.t!=='测试联队');
      [80,78,76,74,72,70,68,66,64,62,60,58].forEach(o=>{
        S.world.nba.push({n:'T'+o,o:o,t:'测试联队',p:'SF',a:25,role:'bench'});
      });
    })();
  `);
  const r1 = JSON.parse(win.eval(`JSON.stringify({
    rs:rosterStr('nba','测试联队'),
    ts6:teamStrength('nba','测试联队',6),
    ts10:teamStrength('nba','测试联队',10)
  })`));
  check('前10人平均 → rosterStr = 4.15（71 均值映射）', near(r1.rs, 4.15), String(r1.rs));
  check('权重 30/70：base 6 → 4.705（旧口径会是 4.983）', near(r1.ts6, 4.705, 1e-6), String(r1.ts6));
  check('权重断点：base 10 → 5.905（旧口径会是 6.783）', near(r1.ts10, 5.905, 1e-6), String(r1.ts10));

  /* 边界①：把第 11、12 人换成 30——排不进前 10，结果必须不变 */
  win.eval(`
    (function(){
      const t=S.world.nba.filter(p=>p.t==='测试联队');
      t.filter(p=>p.o===60||p.o===58).forEach(p=>{p.o=30;});
    })();
  `);
  const r2 = win.eval(`rosterStr('nba','测试联队')`);
  check('第 11/12 人影响不到结果（采样确为前 10）', near(r2, 4.15), String(r2));

  /* 边界②：加一个 99 的尖子——进前 10 后均值 = (99+80+…+64)/10 = 74.7 → 6.925 */
  win.eval(`S.world.nba.push({n:'T99',o:99,t:'测试联队',p:'C',a:25,role:'start'});`);
  const r3 = win.eval(`rosterStr('nba','测试联队')`);
  check('第 11 人若是 99 会进前 10（均值 74.7 → 6.925）', near(r3, 6.925), String(r3));

  /* 边界③：阵容 <5 人 → 纯底子 */
  const r4 = win.eval(`
    (function(){
      S.world.nba=S.world.nba.filter(p=>p.t!=='孤儿队');
      [70,60,50].forEach(o=>S.world.nba.push({n:'O'+o,o:o,t:'孤儿队',p:'SF',a:25,role:'bench'}));
      return teamStrength('nba','孤儿队',7.7);
    })()
  `);
  check('阵容不足 5 人 → 退回纯底子 7.7', near(r4, 7.7), String(r4));

  check('新采样就位（slice(0,10)）', html.indexOf('sort((a,b)=>b.o-a.o).slice(0,10)') >= 0);
  check('新权重就位（*.3+rs*.7）', html.indexOf('(base||6)*.3+rs*.7') >= 0);
  check('旧权重已移除（*.45+rs*.55）', html.indexOf('(base||6)*.45+rs*.55') < 0);
  check('面板文案同口径（前 10 人均值）', html.indexOf('前 10 人均值') >= 0 && html.indexOf('前 8 人均值') < 0);
});
