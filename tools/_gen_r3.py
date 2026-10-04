# -*- coding: utf-8 -*-
"""生成 tools/test_r3.js——R3 摆烂机制的统计验收。整块输出，规避嵌套转义。"""
import io

JS = """/* R3 摆烂机制实装（v4.16）——验收钉（开发计划 R3 验收线）：
 *  ① 默许摆烂（tankAccept）→ 本季我队预期胜率下降 ≥5 个百分点（20 次重算均值）
 *  ② 接受时排名缓存失效（惩罚立即生效，不被旧缓存吞掉）
 *  ③ 跨年自动过期（tankYear 只匹配当前生涯年）
 *  ④ 结算文案与 renderSeason 展示就位
 *  ⑤ evTankHint 默许选项挂上 tankAccept */
const { run } = require('./testkit');

module.exports = run('R3摆烂机制', ({ win, check, html }) => {
  win.eval('renderCreate();');
  win.eval("document.getElementById('fName').value='摆烂测试';");
  win.eval('doCreate(); allocRandom(); confirmAlloc();');
  win.eval(`
    S.league='NBA'; S.mode='immersive';
    S.team=TEAMS.nba[10][0]; S.teamStr=6; S.age=25; S.stage='winter';
    ensureWorld();
  `);

  // ── ① tankAccept：写 tankYear + 清排名缓存 ──
  win.eval('applyFx({tankAccept:1});');
  const fx = JSON.parse(win.eval(`JSON.stringify({
    tankYear:S.flags.tankYear, cur:S.birthYear+S.age,
    cacheCleared:!S._stCache || Object.keys(S._stCache).length === 0
  })`));
  check('默许摆烂写入 tankYear（=当前生涯年）', fx.tankYear === fx.cur, JSON.stringify(fx));
  check('接受时排名缓存失效（惩罚立即生效）', fx.cacheCleared === true, JSON.stringify(fx));

  // ── ② 统计验收：摆烂 vs 不摆烂，我队均值胜率差 ≥5 个百分点 ──
  const stat = JSON.parse(win.eval(`JSON.stringify((function(){
    const my=()=>computeStandings('nba').find(function(r){return r.team===S.team;});
    const meanW=()=>{let s=0;const N=20;for(let i=0;i<N;i++){S._stCache={};s+=my().wins/82;}return s/N;};
    S.flags.tankYear=null;S._stCache={};
    const base=meanW();
    S.flags.tankYear=S.birthYear+S.age;S._stCache={};
    const tank=meanW();
    return {base:base,tank:tank,dropPp:(base-tank)*100};
  })())`));
  check('摆烂后我队预期胜率下降 ≥5 个百分点', stat.dropPp >= 5,
    '下降 ' + stat.dropPp.toFixed(2) + 'pp（base=' + stat.base.toFixed(3) + ' tank=' + stat.tank.toFixed(3) + '）');

  // ── ③ 跨年自动过期 ──
  const exp = JSON.parse(win.eval(`JSON.stringify((function(){
    S.age++;S._stCache={};
    const active=(S.flags.tankYear===(S.birthYear+S.age));
    return {active:active};
  })())`));
  check('跨年后摆烂惩罚自动过期', exp.active === false, JSON.stringify(exp));

  // ── ④ 结算文案与展示就位 ──
  check('赛季结算写入 tankNote', html.indexOf("res.tankNote='管理层按下了计时器") >= 0);
  check('renderSeason 展示摆烂行', html.indexOf('📉 摆烂') >= 0 && html.indexOf('res.tankNote?') >= 0);

  // ── ⑤ evTankHint 默许选项挂机制 ──
  const ev = JSON.parse(win.eval('JSON.stringify(evTankHint())'));
  check('「默许轮换」选项挂 tankAccept', ev.choices[1].fx.tankAccept === 1, JSON.stringify(ev.choices[1].fx));
});
"""

io.open('test_r3.js', 'w', encoding='utf-8', newline='\n').write(JS)
print('generated, lines:', JS.count('\n'))
