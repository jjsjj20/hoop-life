/* 季后赛对抗烈度——对手拔高验收（v4.22.0 首版；v4.23.0 二次加压）：
 * ① NBA 对手 +2.8 ② CBA +4 ③ 欧洲 +1.5 ④ 其他联赛（青训/NCAA）不加压
 * ⑤ 机制注释在产物中 ⑥ 拔高映射就位 */
const { run } = require('./testkit');

module.exports = run('季后赛对抗烈度', ({ win, check, html }) => {
  win.eval('renderCreate();');
  win.eval("document.getElementById('fName').value='烈度测试';");
  win.eval('doCreate(); allocRandom(); confirmAlloc();');

  /* 桩一个对阵图：当前轮 = 首轮，对手（b 侧）纸面实力 6.4 */
  const oppStrOf = lg => Number(win.eval(`
    S.league='${lg}';
    S.bracket={done:false,currentStage:'r1',currentMatch:0,playerSide:'a',playerSeed:2,playerTeam:'我队',
      matches:{playin:[],r1:[{a:{team:'我队',seed:2,str:7.0},b:{team:'对手',seed:7,str:6.4},winner:null}],r2:[],confFinal:[],final:[]}};
    seriesOppStr();
  `));

  const near = (a, b) => Math.abs(a - b) < 1e-9;
  check('NBA：对手 6.4 → 9.2（+2.8）', near(oppStrOf('NBA'), 9.2), oppStrOf('NBA'));
  check('CBA：对手 6.4 → 10.4（+4）', near(oppStrOf('CBA'), 10.4), oppStrOf('CBA'));
  check('欧洲：对手 6.4 → 7.9（+1.5）', near(oppStrOf('欧洲'), 7.9), oppStrOf('欧洲'));
  check('青训/NCAA：不加压（6.4）', near(oppStrOf('青训'), 6.4), oppStrOf('青训'));

  check('机制注释在产物中（对抗烈度）', html.indexOf('季后赛对抗烈度') >= 0);
  check('二次加压映射就位（nba:2.8,cba:4,euro:1.5）', html.indexOf('{nba:2.8,cba:4,euro:1.5}') >= 0);
});
