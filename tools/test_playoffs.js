/* 季后赛 —— 从资格判定到夺冠/出局的完整链路，此前零覆盖
 *
 * 为什么值得测：bracket 是引用/索引套引用/索引的结构（"r1 第 0 场的胜者"），
 * 错一位不会报错，只会让对手凭空变成「（待定）」，或者玩家 1 号种子却抽到 8 号种子的对手。
 * 这里直接把球员塞进各档种子，走完整条链路。
 */
const { run } = require('./testkit');

module.exports = run('季后赛', ({ win, doc, check }) => {
  win.eval('renderCreate();');
  doc.querySelector('#fName').value = '测试';
  win.eval('doCreate(); allocRandom(); confirmAlloc();');
  win.eval("S.league='NBA';S.team='洛杉矶湖人';S.teamStr=8;S.age=26;S.role='player';S.ts=5;ensureWorld();");

  /* 造一张只控制玩家名次的战绩表：同分区其他队按等差数列给胜场，
   * 玩家调到第 N 位，就能精确测各档资格判定 */
  const makeRows = (lg, myRankInConf) => `
    (function(){
      const lg=${JSON.stringify(lg)};
      const conf=${JSON.stringify(win.eval('NBA_CONF[S.team]||null'))};
      const rows=TEAMS[lg].map(t=>({team:t[0],str:t[1],wins:20,losses:62}));
      const same=(conf?TEAMS.nba.map(t=>t[0]).filter(t=>NBA_CONF[t]===conf):TEAMS[lg].map(t=>t[0]));
      const others=same.filter(t=>t!==S.team);
      others.forEach((t,i)=>{rows.find(x=>x.team===t).wins=70-i*4;});
      rows.find(x=>x.team===S.team).wins=71-((${myRankInConf})-1)*4;
      return rows;
    })()`;
  const q = rank => JSON.parse(win.eval(`JSON.stringify(qualify(${makeRows('nba', rank)}))`));

  // ── 资格判定分档 ──────────────────────────────────
  const q1 = q(1), q6 = q(6), q8 = q(8), q10 = q(10), q11 = q(11);
  check('NBA 分区第 1 → 直接晋级', q1 && q1.playin === false && q1.seed === 1, JSON.stringify(q1));
  check('NBA 分区第 6 → 直接晋级（临界）', q6 && q6.playin === false && q6.seed === 6, JSON.stringify(q6));
  check('NBA 分区第 8 → 附加赛（临界）', q8 && q8.playin === true && q8.seed === 8, JSON.stringify(q8));
  check('NBA 分区第 10 → 附加赛（临界）', q10 && q10.playin === true && q10.seed === 10, JSON.stringify(q10));
  check('NBA 分区第 11 → 无缘季后赛', q11 === null, JSON.stringify(q11));
  check('NBA 资格带东西部标签', q1 && q1.conf && /东|西/.test(q1.confLabel || ''), JSON.stringify(q1));

  win.eval("S.league='CBA';S.team='辽宁本钢';");
  const cRows = rank => `(function(){
      const rows=TEAMS.cba.map(t=>({team:t[0],str:t[1],wins:20,losses:32}));
      const others=TEAMS.cba.map(t=>t[0]).filter(t=>t!==S.team);
      others.forEach((t,i)=>{rows.find(x=>x.team===t).wins=70-i*4;});
      rows.find(x=>x.team===S.team).wins=71-((${rank})-1)*4;
      return rows;})()`;
  const c1 = JSON.parse(win.eval(`JSON.stringify(qualify(${cRows(1)}))`));
  const c5 = JSON.parse(win.eval(`JSON.stringify(qualify(${cRows(5)}))`));
  const c12 = JSON.parse(win.eval(`JSON.stringify(qualify(${cRows(12)}))`));
  const c13 = JSON.parse(win.eval(`JSON.stringify(qualify(${cRows(13)}))`));
  check('CBA 第 1 → 直接晋级（1-4 轮空）', c1 && c1.playin === false, JSON.stringify(c1));
  check('CBA 第 5 → 打 12 进 8 附加赛', c5 && c5.playin === true, JSON.stringify(c5));
  check('CBA 第 12 → 附加赛（临界）', c12 && c12.playin === true, JSON.stringify(c12));
  check('CBA 第 13 → 无缘季后赛', c13 === null, JSON.stringify(c13));

  // ── 对阵结构 ─────────────────────────────────────
  const STRUCT = win.eval(`JSON.stringify((function(){
    S.league='NBA';S.team='洛杉矶湖人';
    const B=buildBracket(qualify(${makeRows('nba', 1)}),${makeRows('nba', 1)});
    return {stages:Object.keys(B.matches).map(k=>k+':'+B.matches[k].length).join(' '),
      seed:B.playerSeed,cur:B.currentStage,done:B.done,side:B.playerSide};
  })())`);
  const S1 = JSON.parse(STRUCT);
  check('NBA 对阵含 5 个阶段且各阶段有比赛', /playin:\d+/.test(S1.stages) && /final:1/.test(S1.stages), S1.stages);
  check('1 号种子当前轮次是首轮（不用打附加赛）', S1.cur === 'r1', S1.cur);
  check('对阵建成后选手侧已判定', S1.side === 'a' || S1.side === 'b', S1.side);
  check('1 号种子会推进到分区决赛与总决赛', /confFinal:/.test(S1.stages) && /final:/.test(S1.stages), S1.stages);

  const S8 = JSON.parse(win.eval(`JSON.stringify((function(){
    const B=buildBracket(qualify(${makeRows('nba', 8)}),${makeRows('nba', 8)});
    return {cur:B.currentStage,seed:B.playerSeed};
  })())`));
  check('8 号种子从附加赛打起', S8.cur === 'playin', JSON.stringify(S8));

  const SC = JSON.parse(win.eval(`JSON.stringify((function(){
    S.league='CBA';S.team='辽宁本钢';const rows=${cRows(1)};
    const B=buildBracket(qualify(rows),rows);
    return {stages:Object.keys(B.matches).map(k=>k+':'+B.matches[k].length).join(' '),cur:B.currentStage};
  })())`));
  check('CBA 对阵没有分部决赛', /confFinal:0/.test(SC.stages), SC.stages);

  // ── 夺冠链路：一路赢到底 ──────────────────────────
  const CH = JSON.parse(win.eval(`JSON.stringify((function(){
    S.league='NBA';S.team='洛杉矶湖人';
    const rows=${makeRows('nba', 1)};
    S.bracket=buildBracket(qualify(rows),rows);
    const trace=[];let r=null;
    for(let i=0;i<40;i++){r=bracketPlayerWin();trace.push(r);if(r==='champ'||r==='done')break;}
    return {steps:trace.length,last:r,done:S.bracket.done,seq:trace.join('>'),
      pending:Object.keys(S.bracket.matches).reduce((n,k)=>n+S.bracket.matches[k].filter(m=>!m.winner).length,0)};
  })())`));
  check('一路赢能走到夺冠', CH.last === 'champ', CH.seq);
  check('夺冠后对阵标记结束', CH.done === true);
  check('夺冠后没有未结算的比赛', CH.pending === 0, String(CH.pending));
  check('夺冠链路步数合理（不超过 6 轮）', CH.steps <= 6, CH.steps + ' 步');

  // ── 出局链路 ─────────────────────────────────────
  const LO = JSON.parse(win.eval(`JSON.stringify((function(){
    const rows=${makeRows('nba', 1)};
    S.bracket=buildBracket(qualify(rows),rows);
    const trace=[];let r=null;
    for(let i=0;i<40;i++){r=bracketPlayerLose();trace.push(String(r));if(S.bracket.done)break;}
    return {steps:trace.length,done:S.bracket.done,seq:trace.join('>')};
  })())`));
  check('一路输会被淘汰', LO.done === true, LO.seq);
  check('淘汰链路不无限循环', LO.steps <= 6, LO.steps + ' 步');

  // ── 结果翻译成赛季文案（computeSeason 消费 _playoffResult）──
  const txt = pr => win.eval(`JSON.stringify(computeSeason(${JSON.stringify(pr)},.62,null).playoffs)`);
  check('冠军结果 → 夺冠文案', /冠军/.test(txt({ rounds: 3, champ: true })), txt({ rounds: 3, champ: true }));
  check('止步半决赛 → 对应文案', /半决赛/.test(txt({ rounds: 1, champ: false, level: 'r2' })),
    txt({ rounds: 1, champ: false, level: 'r2' }));
  check('附加赛出局 → 对应文案', /附加赛/.test(txt({ rounds: 0, champ: false, kind: 'playin' })),
    txt({ rounds: 0, champ: false, kind: 'playin' }));
  check('疯狂三月冠军 → 对应文案', /NCAA 冠军/.test(txt({ rounds: 3, champ: true, kind: 'march' })),
    txt({ rounds: 3, champ: true, kind: 'march' }));
  check('无对阵信息时也能兜底出文案', typeof JSON.parse(txt(null)) === 'string', txt(null));

  // ── 模拟整张对阵：不出现「待定」 ─────────────────────
  const SIM = JSON.parse(win.eval(`JSON.stringify((function(){
    S.league='NBA';S.team='洛杉矶湖人';
    const rows=${makeRows('nba', 1)};
    const B=buildBracket(qualify(rows),rows);
    simulateBracketToEnd(B);
    let pending=0,undef=0;
    Object.keys(B.matches).forEach(k=>B.matches[k].forEach(m=>{
      if(!m.winner)pending++;
      const w=sideTeam(B,m,m.winner);
      if(!w||!w.team||w.team.indexOf('待定')>=0)undef++;
    }));
    const f=B.matches.final[0];
    return {pending,undef,champTeam:sideTeam(B,f,f.winner).team};
  })())`));
  check('整张对阵模拟后无未结算比赛', SIM.pending === 0, String(SIM.pending));
  check('对阵里不出现「待定」对手', SIM.undef === 0, String(SIM.undef));
  check('模拟能产出总冠军球队', !!SIM.champTeam && SIM.champTeam.length > 1, SIM.champTeam);
});
