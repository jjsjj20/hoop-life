/* 教练模式 —— 整季循环，此前零覆盖
 *
 * 为什么值得测：教练模式是独立的一条链路（自己的事件池、自己的结算、自己的终章），
 * 却共享 S 与赛季推进。球员线改一处很容易顺手碰坏它，而它没有一行测试。
 *
 * 两个容易写错的语义（本次就是踩了才写清的）：
 *   · startCoach() 只抛合同，球队/联赛要玩家点选后才写入 S.coach
 *   · coachNext() 只推年龄、清事件计数；赛季数由 coachSeasonEnd() 增
 */
const { run } = require('./testkit');

module.exports = run('教练模式', ({ win, doc, check, click }) => {
  win.eval('renderCreate();');
  doc.querySelector('#fName').value = '教练测试';
  win.eval('doCreate(); allocRandom(); confirmAlloc();');

  // ── 开局：抛合同 → 点选球队 ─────────────────────────
  let threw = null;
  try { win.eval('startCoach();'); } catch (e) { threw = e; }
  check('startCoach 不抛异常', !threw, threw && threw.message);
  check('角色切换为教练', win.eval('S.role') === 'coach', win.eval('S.role'));
  const c0 = JSON.parse(win.eval('JSON.stringify(S.coach)'));
  check('开局赛季数 = 1、战绩清零、氛围初始 5',
    c0.season === 1 && c0.wins === 0 && c0.losses === 0 && c0.chem === 5,
    JSON.stringify({ season: c0.season, wins: c0.wins, losses: c0.losses, chem: c0.chem }));
  check('三份合同摆在桌上', win.eval('UI.mode') === 'offers' && (win.eval('UI.offers||[]').length === 3),
    win.eval('UI.mode') + ' / ' + win.eval('(UI.offers||[]).length'));

  const offerBtns = doc.querySelectorAll('#chs .ch');
  check('合同按钮已渲染', offerBtns.length === 3, String(offerBtns.length));
  click(offerBtns[0]);
  check('点选后写入球队与联赛',
    !!win.eval('S.coach.team') && /CBA|NBA|欧洲/.test(win.eval('S.coach.league') || ''),
    win.eval('S.coach.team') + ' / ' + win.eval('S.coach.league'));
  check('点选后进入教练事件', win.eval('UI.mode') === 'coachEv', win.eval('UI.mode'));

  const ev = JSON.parse(win.eval('JSON.stringify(coachEvent())'));
  check('教练事件有标题/正文/选项',
    !!ev.title && (ev.scene || '').length > 20 && ev.choices.length >= 2 && ev.choices.length <= 4,
    ev.title + ' / ' + ev.choices.length + ' 选项');

  // 打完当前这一季：每个事件「选一个 → 继续」，直到赛季结算
  const playSeason = extra => win.eval(`(function(){
    let guard=0;
    while(UI&&UI.mode==='coachEv'&&guard++<20){
      coachChoose(R.int(0,UI.ev.choices.length-1));
      if(UI&&UI.mode==='coachEv')coachAdvance();
    }
    ${extra || ''}
    return JSON.stringify({mode:UI&&UI.mode,season:S.coach.season,wins:S.coach.wins,losses:S.coach.losses,
      evDone:S.coach.evDone,picks:S.coach.picks.length,
      pickOvr:S.coach.picks.length?S.coach.picks[S.coach.picks.length-1].o:null,
      stLg:S.standings&&S.standings.lg,stRows:S.standings&&S.standings.rows?S.standings.rows.length:0});
  })()`);

  let s1 = null, err1 = null;
  try { s1 = JSON.parse(playSeason()); } catch (e) { err1 = e; }
  check('走完一整季不抛异常', !err1, err1 && err1.message);
  check('赛季结束后离开了事件循环', s1 && s1.mode !== 'coachEv', s1 && s1.mode);
  const games = win.eval("S.coach.league==='NBA'?82:34");
  check('战绩场次合计 = 联赛场次数', s1 && (s1.wins + s1.losses) === games,
    s1 && (s1.wins + '胜' + s1.losses + '负 / 应为 ' + games + ' 场'));
  check('战绩是有效数字（不是 NaN）', s1 && Number.isFinite(s1.wins) && Number.isFinite(s1.losses),
    JSON.stringify(s1 && { wins: s1.wins, losses: s1.losses }));
  check('记录了一名选秀新人且综评在区间内',
    s1 && s1.picks === 1 && s1.pickOvr >= 42 && s1.pickOvr <= 88,
    JSON.stringify({ picks: s1 && s1.picks, ovr: s1 && s1.pickOvr }));
  check('写了联赛排名快照',
    s1 && s1.stLg && s1.stRows === ({ nba: 30, cba: 20, euro: 10 }[s1.stLg] || -1),
    JSON.stringify({ lg: s1 && s1.stLg, rows: s1 && s1.stRows }));

  // ── 重复结算保护：同一个事件连点两次只生效一次 ────────
  const dbl = win.eval(`(function(){
    UI={mode:'coachEv',ev:coachEvent(),coachDone:false};
    coachChoose(0);
    const mid=JSON.stringify({tac:S.coach.tac,mot:S.coach.mot,eye:S.coach.eye,chem:S.coach.chem});
    coachChoose(0);
    const end=JSON.stringify({tac:S.coach.tac,mot:S.coach.mot,eye:S.coach.eye,chem:S.coach.chem});
    return mid===end;
  })()`);
  check('同一事件连点两次只结算一次', dbl === true, String(dbl));

  // ── 连推 5 个完整赛季：每轮 = coachNext() + 打完这一季 ──
  const seq = [];
  let thrown = null;
  try {
    for (let i = 0; i < 5; i++) {
      const before = JSON.parse(win.eval('JSON.stringify({age:S.age,season:S.coach.season,wins:S.coach.wins,honors:S.coach.honors.length})'));
      win.eval('coachNext();');
      const mid = JSON.parse(win.eval('JSON.stringify({age:S.age,season:S.coach.season,evDone:S.coach.evDone})'));
      check(`第 ${i + 2} 轮：coachNext 只推年龄、清事件计数（不增赛季数）`,
        mid.age === before.age + 1 && mid.season === before.season && mid.evDone === 0,
        JSON.stringify({ age: mid.age, season: mid.season, evDone: mid.evDone }));
      const after = JSON.parse(playSeason()).season
        ? JSON.parse(win.eval('JSON.stringify({season:S.coach.season,wins:S.coach.wins,losses:S.coach.losses,picks:S.coach.picks.length,honors:S.coach.honors.length})'))
        : null;
      seq.push(after);
      check(`第 ${i + 2} 轮：打完一季后赛季数 +1`, after.season === before.season + 1,
        before.season + '→' + after.season);
      check(`第 ${i + 2} 轮：累计胜场只增不减`, after.wins >= before.wins, before.wins + '→' + after.wins);
      check(`第 ${i + 2} 轮：战绩是有效数字`, Number.isFinite(after.wins) && Number.isFinite(after.losses));
      check(`第 ${i + 2} 轮：选秀新人记录保留最近 3 名`, after.picks >= 1 && after.picks <= 3, String(after.picks));
    }
  } catch (e) { thrown = e; }
  check('连推 5 季不抛异常', !thrown, thrown && thrown.message);
  check('赛季数一路递增且无跳号',
    seq.every((s, i) => i === 0 || s.season === seq[i - 1].season + 1),
    seq.map(s => s.season).join('→'));

  // ── 存档往返 ─────────────────────────────────────
  const snap = JSON.parse(win.eval('JSON.stringify({season:S.coach.season,wins:S.coach.wins,losses:S.coach.losses,role:S.role,chem:S.coach.chem})'));
  win.eval('save();S=null;UI=null;');
  win.eval(`(function(){const d=JSON.parse(localStorage.getItem(CFG.SAVE_KEY));S=d.S;ensureState();})()`);
  const back = JSON.parse(win.eval('JSON.stringify({season:S.coach.season,wins:S.coach.wins,losses:S.coach.losses,role:S.role,chem:S.coach.chem})'));
  Object.keys(snap).forEach(k => check('读档后教练 ' + k + ' 一致', back[k] === snap[k],
    JSON.stringify(snap[k]) + ' → ' + JSON.stringify(back[k])));

  // ── 终章 ─────────────────────────────────────────
  win.eval('coachQuit();');
  check('coachQuit 进入终章界面', win.eval('UI.mode') === 'end' && win.eval('UI.endMode') === 'coach',
    win.eval('UI.mode') + '/' + win.eval('UI.endMode'));
  let endThrew = null;
  try { win.eval('showEnd();'); } catch (e) { endThrew = e; }
  check('教练终章能渲染', !endThrew, endThrew && endThrew.message);
  check('终章页面有内容', (doc.querySelector('#app').innerHTML || '').length > 300);
  check('教练评语可生成', (win.eval('coachReview().title') || '').length > 1, win.eval('coachReview().title'));
});
