/* 戏剧配额防饿死（step ⑧ / M1 调参）的行为测试
 *
 * 场景：本季缺戏（need>0），而「题材未重复」的候选里已经没有戏剧事件。
 *
 * 修复前：finalPool=freshTopic（非空但全是流水账）→ 9:1 加权没戏剧可加，
 *         戏剧配额永远喂不饱（M1 实测全季戏剧占比 28.9%）。
 * 修复后：允许戏剧事件从 freshAll 撞题材出场 → 首抽必为戏剧。
 * 同时钉住另一面：不缺戏（need≤0）时兜底绝不触发。
 *
 * v4.13 起戏剧事件横跨 9 个题材，旧的「标记全部戏剧题材」布景不再可行
 * （会把 freshTopic 清空）——改为精确控制：把池内其他事件全部标进 S.used，
 * 只留 2 条流水账（题材未用）+ 1 条戏剧（题材已用）。
 */
const { run } = require('./testkit');

module.exports = run('戏剧配额', ({ win, check }) => {
  // ── 开一局真实的 NBA 生涯，拿到完整的 S 结构 ──
  win.eval('renderCreate();');
  win.eval("document.getElementById('fName').value='配额测试';");
  win.eval('doCreate(); allocRandom(); confirmAlloc();');
  win.eval(`
    S.league='NBA'; S.mode='immersive';
    S.team=TEAMS.nba[0][0]; S.teamStr=6; S.age=18; S.stage='spring';
    S.stageDone=0; S.stageNeed=stageNeedFor();
    ensureWorld(); if(isPro()&&!S.contract)setContract(S.team,S.league,2,'职业合同');
  `);

  // ── 布景：池内只留「2 条流水账 + 1 条戏剧（题材已用）」可抽 ──
  const prep = JSON.parse(win.eval(`JSON.stringify((function(){
    const pool=POOLS[poolKey()]||POOLS.spring;
    const ok=e=>!GATED[e.id]||GATED[e.id]();
    const all=pool.filter(ok);
    const drama=all.filter(function(e){return evKindOf(e)==='drama';});
    const routines=all.filter(function(e){return evKindOf(e)!=='drama';});
    if(drama.length<1||routines.length<2)return {err:'pool too small'};
    const dTgt=drama[0],r1=routines[0],r2=routines[1];
    S.used={};S.used[poolKey()]=[];
    pool.forEach(function(e){if(e!==dTgt&&e!==r1&&e!==r2)S.used[poolKey()].push(e.id);});
    S.recent={};
    S.usedTopics=[evTopicOf(dTgt)];           /* 戏剧的题材标记为已用 → freshTopic 无戏剧 */
    S.evY=S.birthYear+S.age;S.evSeen=1;S.evDrama=0;   /* 缺戏：need=round(1.35)-0=1>0 */
    const year=evSeasonCounters();
    /* 候选集已由 S.used 精确控制为 {dTgt,r1,r2}；freshAll/freshTopic 直接从三者推得 */
    const freshAll=[dTgt,r1,r2];
    const freshTopic=freshAll.filter(function(e){return S.usedTopics.indexOf(evTopicOf(e))<0;});
    return {dId:dTgt.id,dTopic:evTopicOf(dTgt),dramaN:drama.length,
            freshTopicN:freshTopic.length,
            freshTopicHasDrama:freshTopic.some(function(e){return evKindOf(e)==='drama';}),
            freshAllHasDrama:freshAll.some(function(e){return evKindOf(e)==='drama';}),
            need:Math.round((S.evSeen+1)*EV_DRAMA_SHARE)-S.evDrama};
  })())`));

  check('池子里有可抽的戏剧事件（≥5）', prep.dramaN >= 5, '实际 ' + prep.dramaN + ' 条');
  check('布景：freshTopic 恰为 2 条流水账且无戏剧', prep.freshTopicN === 2 && !prep.freshTopicHasDrama,
    'freshTopic=' + prep.freshTopicN + ' 条，含戏剧=' + prep.freshTopicHasDrama);
  check('布景：freshAll 里仍有戏剧', prep.freshAllHasDrama);
  check('布景：本季缺戏（need>0）', prep.need > 0, 'need=' + prep.need);

  // ── 断言一：缺戏 + 题材耗尽 → 首抽必为戏剧（撞题材兜底生效）──
  const first = JSON.parse(win.eval(`JSON.stringify((function(){
    const e=pickGeneric();
    return {id:e.id, kind:evKindOf(e), topic:evTopicOf(e),
            seen:S.evSeen, dramaCnt:S.evDrama, recentHit:S.recent[e.id],
            hasChoices:Array.isArray(e.choices)&&e.choices.length>0};
  })())`));
  check('缺戏时首抽即为戏剧事件', first.kind === 'drama', '抽到 ' + first.id + '（' + first.kind + '）');
  check('兜底精确命中：抽到的正是布景里那 条戏剧', first.id === prep.dId,
    first.id + ' vs ' + prep.dId);
  check('兜底允许撞题材：该戏剧的题材本季已出现过', first.topic === prep.dTopic,
    first.topic + ' vs ' + prep.dTopic);
  check('戏剧计数 S.evDrama 已 +1（累计 1）', first.dramaCnt === 1, 'S.evDrama=' + first.dramaCnt);
  check('事件计数 S.evSeen 已 +1（累计 2）', first.seen === 2, 'S.evSeen=' + first.seen);
  check('4 年记忆已记录（S.recent[id]=当年）', first.recentHit === win.eval('S.birthYear+S.age'));
  check('返回的事件已物化（带选项）', first.hasChoices);

  // ── 断言二：不缺戏（need≤0）时兜底绝不触发 → 抽到非戏剧 ──
  const second = JSON.parse(win.eval(`JSON.stringify((function(){
    S.evSeen=3; S.evDrama=3;   /* need=round(4*0.45)-3=2-3=-1≤0 */
    const e=pickGeneric();
    return {id:e.id, kind:evKindOf(e)};
  })())`));
  check('不缺戏时兜底不触发：抽到非戏剧', second.kind === 'routine',
    '抽到 ' + second.id + '（' + second.kind + '）');

  // ── 断言三：常规情况不受影响——题材未重复时照样优先题材内候选 ──
  const third = JSON.parse(win.eval(`JSON.stringify((function(){
    S.used={}; S.recent={}; S.usedTopics=[]; S.evSeen=0; S.evDrama=0;
    const e=pickGeneric();
    return {id:e.id, kind:evKindOf(e), topic:evTopicOf(e), topics:S.usedTopics.slice()};
  })())`));
  check('常规首抽会把新题材记入本季记忆', third.topics.indexOf(third.topic) >= 0,
    'topics=' + JSON.stringify(third.topics) + ' topic=' + third.topic);
  check('常规路径抽到的事件进入了 4 年记忆',
    win.eval("JSON.stringify(Object.keys(S.recent))").indexOf('"' + third.id + '"') >= 0);
});
