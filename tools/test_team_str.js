/* 球队实力模型——前13人取样 + 权重 80/20 + 取样深度补偿 验收（v4.25.0）：
 * ① rosterStr 取前 13 人平均（第 14 人之后不影响结果）
 * ② teamStrength 权重 = 底子 20% + 阵容 80%（用 base 断点值验证）
 * ③ 取样深度补偿：长名单（>13 人）补 2.2 映射分；短名单（≤13 人）不补
 * ④ 阵容人数不足 5 人退回纯底子（旧行为保留）
 * ⑤ 产物字符串断言（新公式就位、旧公式移除、面板文案同口径） */
const { run } = require('./testkit');

module.exports = run('球队实力模型', ({ win, check, html }) => {
  win.eval('renderCreate();');
  win.eval("document.getElementById('fName').value='实力测试';");
  win.eval('doCreate(); allocRandom(); confirmAlloc();');
  win.eval("S.league='NBA'; ensureWorld();");

  const near = (a, b, eps) => Math.abs(a - b) < (eps || 1e-9);

  /* 长名单合成阵容（15 人）：顶 13 人均值 72 → rosterStr = 6.4+(72−74)×.75+2.2 = 7.1 */
  win.eval(`
    (function(){
      S.world.nba=S.world.nba.filter(p=>p.t!=='测试联队'&&p.t!=='短名单队'&&p.t!=='孤儿队');
      [84,82,80,78,76,74,72,70,68,66,64,62,60,40,38].forEach(o=>{
        S.world.nba.push({n:'T'+o,o:o,t:'测试联队',p:'SF',a:25,role:'bench'});
      });
    })();
  `);
  const r1 = JSON.parse(win.eval(`JSON.stringify({
    rs:rosterStr('nba','测试联队'),
    ts6:teamStrength('nba','测试联队',6),
    ts10:teamStrength('nba','测试联队',10)
  })`));
  check('前13人平均 → rosterStr = 7.1（72 均值 + 深度补偿 2.2）', near(r1.rs, 7.1, 1e-6), String(r1.rs));
  check('权重 20/80：base 6 → 6.88', near(r1.ts6, 6.88, 1e-6), String(r1.ts6));
  check('权重断点：base 10 → 7.68（旧权重 30/70 会是 7.97）', near(r1.ts10, 7.68, 1e-6), String(r1.ts10));

  /* 边界①：第 15 人（38）改动——排不进前 13，结果必须不变 */
  win.eval(`
    (function(){
      const t=S.world.nba.filter(p=>p.t==='测试联队');
      t.filter(p=>p.o===38).forEach(p=>{p.o=30;});
    })();
  `);
  const r2 = win.eval(`rosterStr('nba','测试联队')`);
  check('第 15 人影响不到结果（采样确为前 13）', near(r2, 7.1, 1e-6), String(r2));

  /* 边界②：第 14 人（40）提到 70——挤进前 13 后均值 946/13=72.769 → 7.677 */
  win.eval(`
    (function(){
      const t=S.world.nba.filter(p=>p.t==='测试联队');
      t.filter(p=>p.o===40).forEach(p=>{p.o=70;});
    })();
  `);
  const r3 = win.eval(`rosterStr('nba','测试联队')`);
  check('第 14 人挤进前 13 会改变结果（均值 72.77 → 7.677）', near(r3, 7.677, 1e-3), String(r3));

  /* 边界③：短名单（12 人 ≤13）——取样即全队，无深度补偿：均值 73 → 5.65 */
  win.eval(`
    (function(){
      [84,82,80,78,76,74,72,70,68,66,64,62].forEach(o=>{
        S.world.nba.push({n:'S'+o,o:o,t:'短名单队',p:'SG',a:25,role:'bench'});
      });
    })();
  `);
  const r4 = win.eval(`rosterStr('nba','短名单队')`);
  check('短名单不补偿（12 人均值 73 → 5.65）', near(r4, 5.65, 1e-6), String(r4));

  /* 边界④：阵容 <5 人 → 纯底子 */
  const r5 = win.eval(`
    (function(){
      [70,60,50].forEach(o=>S.world.nba.push({n:'O'+o,o:o,t:'孤儿队',p:'SF',a:25,role:'bench'}));
      return teamStrength('nba','孤儿队',7.7);
    })()
  `);
  check('阵容不足 5 人 → 退回纯底子 7.7', near(r5, 7.7), String(r5));

  check('新采样就位（slice(0,13)）', html.indexOf('sort((a,b)=>b.o-a.o).slice(0,13)') >= 0);
  check('深度补偿就位（>13 人补 2.2）', html.indexOf('rs.length>13?2.2:0') >= 0);
  check('新权重就位（*.2+rs*.8）', html.indexOf('(base||6)*.2+rs*.8') >= 0);
  check('旧权重已移除（*.3+rs*.7）', html.indexOf('(base||6)*.3+rs*.7') < 0);
  check('面板文案同口径（前 13 人均值）', html.indexOf('前 13 人均值') >= 0 && html.indexOf('前 10 人均值') < 0);
});
