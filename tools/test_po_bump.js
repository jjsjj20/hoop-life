/* v4.22.0 季后赛对抗烈度——对手拔高验收：
 * ① NBA 对手 +1.5 ② CBA +2.5 ③ 欧洲 +1.0 ④ 其他联赛（青训/NCAA）不加压
 * ⑤ 机制注释在产物中 ⑥ 系列赛单场构造确实吃到拔高后的 oppStr */
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
  check('NBA：对手 6.4 → 7.9（+1.5）', near(oppStrOf('NBA'), 7.9), oppStrOf('NBA'));
  check('CBA：对手 6.4 → 8.9（+2.5）', near(oppStrOf('CBA'), 8.9), oppStrOf('CBA'));
  check('欧洲：对手 6.4 → 7.4（+1.0）', near(oppStrOf('欧洲'), 7.4), oppStrOf('欧洲'));
  check('青训/NCAA：不加压（6.4）', near(oppStrOf('青训'), 6.4), oppStrOf('青训'));

  check('机制注释在产物中（对抗烈度）', html.indexOf('季后赛对抗烈度') >= 0);
  check('拔高映射就位（nba:1.5,cba:2.5,euro:1）', html.indexOf('{nba:1.5,cba:2.5,euro:1}') >= 0);
});
