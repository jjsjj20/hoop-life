/* 老存档迁移 —— 玩家最容易被坑、也最难人工复现的路径
 *
 * 为什么值得测：这个项目跨了 21 个版本，字段是逐版本加上去的（skills / shot / tend /
 * world / draft / worldHistory / injSites…）。老档缺字段时如果某处漏了兜底，
 * 玩家读到一半会崩，而你本地永远复现不了——因为你手上只有最新存档。
 * 这里用「把最新档删掉一批字段」的方式造出各年形态的老档，逐个走 load+ensureState。
 */
const { run } = require('./testkit');

module.exports = run('老存档迁移', ({ win, doc, check }) => {
  win.eval('renderCreate();');
  doc.querySelector('#fName').value = '迁移测试';
  win.eval('doCreate(); allocRandom(); confirmAlloc();');
  win.eval("S.league='CBA';S.team='辽宁本钢';S.teamStr=7;S.age=27;ensureWorld();");

  const KEY = win.eval('CFG.SAVE_KEY');

  /* 造老档：以真实 freshState 为底，删掉指定的"后来才加的"字段 */
  const makeLegacy = (dropJs, patchJs) => win.eval(`JSON.stringify((function(){
    const s=freshState({name:'老档球员',birthYear:1998,prov:'广东',city:'广州',pos:'SG',height:192,wingspan:200,weight:88});
    s.age=27;s.league='CBA';s.team='辽宁本钢';s.teamStr=7;s.career={seasons:6,pts:5000,reb:1200,ast:900};
    s.honors=[{y:'2024-25赛季',t:'全明星'}];s.log=[{y:'2024-25赛季',t:'首秀'}];
    ${dropJs || ''}
    ${patchJs || ''}
    return {v:1,S:s};
  })())`);

  /* probe 是**表达式**，它的值会被返回出去（早先当成语句插进去，值被丢掉了） */
  const loadIt = (raw, probe) => win.eval(`(function(){
    localStorage.removeItem(CFG.SAVE_KEY);
    localStorage.setItem(CFG.SAVE_KEY, ${JSON.stringify(raw)});
    S=null;UI=null;
    const d=load();
    if(!d)return JSON.stringify({loadFailed:true});
    S=d;ensureState();
    return (${probe || "JSON.stringify({ok:true})"});
  })()`);

  const PROBE = `(function(){
    const T=k=>{const v=S[k];return v===null?'null':v===undefined?'undefined':Array.isArray(v)?'array':typeof v;};
    return JSON.stringify({
      ok: true,
      skills: S.skills?Object.keys(S.skills).length:0,
      shot: T('shot'), tend: T('tend'), historyLen: (S.history||[]).length,
      careerStl: S.career.stl, careerFga: S.career.fga,
      world: T('world'), used: T('used'), recent: T('recent'), usedTopics: T('usedTopics'),
      draft: T('draft'), standings: T('standings'), bracket: T('bracket'),
      campNull: S.camp===null, injuryNull: S.injury===null,
      mode: S.mode, evY: typeof S.evY, flags: T('flags'), played: T('played'),
      injSites: T('injSites'), worldHistory: T('worldHistory'), stageTotal: S.stageTotal
    });
  })()`;

  // ── 1. 极简老档：把一批后加字段全删掉 ──────────────────
  const DROP = `['skills','shot','tend','tendAll','history','world','draft','standings','bracket',
    'injury','injSites','camp','worldHistory','rivals','used','recent','usedTopics','flags','played',
    'mode','stageTotal','worldNews','lastLossTeam','injuryMissed','injuryMissedBase'].forEach(k=>{delete s[k];});
    delete s.career.stl;delete s.career.blk;delete s.career.fga;delete s.career.fgm;
    delete s.career.tpa;delete s.career.tpm;delete s.career.fta;delete s.career.ftm;`;
  let err = null, p = null;
  try { p = JSON.parse(loadIt(makeLegacy(DROP), PROBE)); } catch (e) { err = e; }
  check('极简老档迁移不抛异常', !err, err && err.message);
  check('老档能被读出', p && p.ok === true, JSON.stringify(p && p.loadFailed));
  if (p && p.ok) {
    check('缺失的 skills 被回推补齐（15 项，v4.28.0 补罚球/抢断/力量/速度）', p.skills === 15, String(p.skills));
    check('缺失的 shot 被补齐为对象', p.shot === 'object', p.shot);
    check('缺失的 tend / history 被补齐', p.tend === 'object' && p.historyLen === 0, p.tend + '/' + p.historyLen);
    check('career 里后加的防守/出手字段补 0',
      p.careerStl === 0 && p.careerFga === 0, JSON.stringify({ stl: p.careerStl, fga: p.careerFga }));
    // 注意分工：ensureState 只补状态字段，球员世界由 ensureWorld 负责——
    // 所以这里 world 是 undefined 属**正确行为**，单独验 ensureWorld 能补出来。
    check('ensureState 不管球员世界（交给 ensureWorld）', p.world === 'undefined', p.world);
    const w = win.eval('(function(){ensureWorld();let n=0;for(const k in S.world)n+=S.world[k].length;return n;})()');
    check('ensureWorld 能为老档补出球员世界', w > 500, w + ' 人');
    check('used / recent / usedTopics 被补齐',
      p.used === 'object' && p.recent === 'object' && p.usedTopics === 'array',
      [p.used, p.recent, p.usedTopics].join('/'));
    check('draft / standings / bracket 补为 null 而不是 undefined',
      p.draft === 'null' && p.standings === 'null' && p.bracket === 'null',
      [p.draft, p.standings, p.bracket].join('/'));
    check('camp / injury 补为 null', p.campNull === true && p.injuryNull === true);
    check('mode 补为沉浸模式', p.mode === 'immersive', String(p.mode));
    check('evY 补为数字', p.evY === 'number', p.evY);
    check('flags / played / injSites / worldHistory 被补齐',
      p.flags === 'object' && p.played === 'array' && p.injSites === 'object' && p.worldHistory === 'array',
      [p.flags, p.played, p.injSites, p.worldHistory].join('/'));
    check('stageTotal 补为 0', p.stageTotal === 0, String(p.stageTotal));
    check('关键身份字段不被迁移破坏',
      win.eval('S.name') === '老档球员' && win.eval('S.age') === 27 && win.eval('S.team') === '辽宁本钢',
      win.eval('S.name') + '/' + win.eval('S.age') + '/' + win.eval('S.team'));
    check('迁移后仍可序列化（能被再次存档）',
      typeof win.eval('saveJson()') === 'string' && win.eval('saveJson()').length > 1000);
  }

  // ── 2. v1 形状：界面状态挂在 S.ui 上 ───────────────────
  const v1 = JSON.parse(loadIt(makeLegacy(DROP, "s.ui={mode:'event',ev:null};"),
    "JSON.stringify({ok:true,uiMode:UI&&UI.mode,suiType:typeof S.ui})"));
  check('v1 老档（界面状态在 S.ui）能读', v1.ok === true, JSON.stringify(v1));
  check('S.ui 被搬到 UI 并从存档里摘掉', v1.uiMode === 'event' && v1.suiType === 'undefined',
    'UI=' + v1.uiMode + ' / S.ui=' + v1.suiType);

  // ── 3. 脏数据：重复/空值的 played ─────────────────────
  const dirty = JSON.parse(loadIt(
    makeLegacy('', "s.played=['辽宁本钢',null,'辽宁本钢','','广东华南虎',undefined];"),
    "JSON.stringify({ok:true,played:S.played})"));
  check('脏 played 被清洗（去空去重）',
    dirty.ok === true && JSON.stringify(dirty.played) === '["辽宁本钢","广东华南虎"]',
    JSON.stringify(dirty.played));

  // ── 4. 损坏的存档：不能抛异常 ─────────────────────────
  const bad1 = win.eval(`(function(){localStorage.setItem(CFG.SAVE_KEY,'{不是合法 JSON');S=null;UI=null;return load()===null;})()`);
  check('损坏的 JSON 不抛异常，返回 null', bad1 === true, String(bad1));
  const bad2 = win.eval(`(function(){localStorage.setItem(CFG.SAVE_KEY,'{"v":1}');S=null;UI=null;return load()===null;})()`);
  check('没有 S 字段的文档返回 null', bad2 === true, String(bad2));
  const bad3 = win.eval(`(function(){localStorage.removeItem(CFG.SAVE_KEY);S=null;UI=null;return load()===null;})()`);
  check('没有存档时返回 null', bad3 === true, String(bad3));

  // ── 5. 不完整的选秀数据能自愈（v4.9.5 修的同类问题）────
  const heal = win.eval(`JSON.stringify((function(){
    localStorage.removeItem(CFG.SAVE_KEY);
    localStorage.setItem(CFG.SAVE_KEY, JSON.stringify({v:1,S:(function(){
      const s=freshState({name:'半途存档',birthYear:2008,prov:'广东',city:'广州',pos:'SG',height:190,wingspan:198,weight:85});
      s.age=20;s.league='CBA';s.team='辽宁本钢';s.teamStr=7;
      s.draft={stock:20,order:TEAMS.nba.map(t=>t[0]),promise:null,pick:null,y:'2028-29赛季'};  /* 缺 draw/lotto/slot */
      return s;})()}));
    S=null;UI=null;const d=load();S=d;ensureState();
    const before=Object.keys(S.draft).join(',');
    ensureDraft();
    const after=S.draft;
    return {before:before,hasDraw:!!after.draw,hasLotto:!!after.lotto,hasSlot:!!after.slot,orderLen:after.order.length};
  })())`);
  const H = JSON.parse(heal);
  check('半途存档的 draft 缺抽签数据', !/draw/.test(H.before), H.before);
  check('ensureDraft 自愈补齐抽签数据', H.hasDraw && H.hasLotto && H.hasSlot, JSON.stringify(H));
  check('自愈后签位表长度正确', H.orderLen === 30, String(H.orderLen));

  // ── 6. v4.10：老教练存档就地「光荣退役」（教练模式已整体移除）──
  const coach = JSON.parse(loadIt(
    makeLegacy('', `s.role='coach';s.usedCoach=['c1','c2'];
      s.coach={tac:70,mot:66,eye:72,chem:6,season:3,honors:[{y:'2026-27赛季',t:'辽宁本钢 冠军'}],wins:80,losses:60,evDone:1,picks:[],team:'辽宁本钢',str:7,league:'CBA'};`),
    "JSON.stringify({ok:true,uiMode:UI&&UI.mode,retired:S.retired===true,coachGone:typeof S.coach,roleGone:typeof S.role,usedCoachGone:typeof S.usedCoach})"));
  check('老教练存档迁移不抛异常', coach.ok === true, JSON.stringify(coach));
  check('老教练档就地退役（S.retired=true）', coach.retired === true, String(coach.retired));
  check('读档后落到生涯终章页（UI.mode=end）', coach.uiMode === 'end', String(coach.uiMode));
  check('S.coach / S.role / S.usedCoach 字段被清除',
    coach.coachGone === 'undefined' && coach.roleGone === 'undefined' && coach.usedCoachGone === 'undefined',
    JSON.stringify(coach));

  // ── 7. 迁移 + 存档往返：字段不再丢 ─────────────────────
  win.eval('ensureState();ensureWorld();');   /* 上一个用例把 S 换成了缺世界的半途存档，先补全 */
  const round = win.eval(`JSON.stringify((function(){
    save();const j=saveJson();const before=JSON.parse(j).S;
    S=null;UI=null;const d=load();S=d;ensureState();
    const keys=['name','age','team','league','pos','mode','evY','stageTotal'];
    const diff=keys.filter(k=>JSON.stringify(before[k])!==JSON.stringify(S[k]));
    return {diff:diff,skills:Object.keys(S.skills||{}).length,world:!!S.world};
  })())`);
  const RT = JSON.parse(round);
  check('迁移后存档往返字段一致', RT.diff.length === 0, RT.diff.join(','));
  check('往返后技能表仍完整（15 项，v4.28.0 新体系）', RT.skills === 15, String(RT.skills));
  check('往返后球员世界仍在', RT.world === true);
});
