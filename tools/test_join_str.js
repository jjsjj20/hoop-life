/* 加盟强度快照回正 —— 「有玩家在的球队强度立马提升」修复验收（v4.27.5）：
 * ① joinTeamStr = 该队动态账面（与 teamStrength 一致，不再取静态底子）
 * ② 找不到的队（青训）→ fallback；world 未生成 → 回退底子（等价旧行为）
 * ③ setJoinStr 写入动态值 + 标记 _joinV2
 * ④ 老档迁移：底子 → 动态账面（一次性、幂等）；_joinV2 已设不再动
 * ⑤ 产物字符串断言：9 处加盟路径改写就位、旧写法清零、迁移段就位 */
const { run } = require('./testkit');

module.exports = run('加盟强度快照', ({ win, check, html }) => {
  win.eval('renderCreate();');
  win.eval("document.getElementById('fName').value='加盟测试';");
  win.eval('doCreate(); allocRandom(); confirmAlloc();');
  win.eval("S.league='NBA';S.team=TEAMS.nba[1][0];S.teamStr=9;S.age=27;S.stage='winter';S.starter=true;ensureWorld();");

  /* ① joinTeamStr = 动态账面（与「查看其他球队」显示同口径） */
  const r1 = JSON.parse(win.eval(`(()=>{const t=TEAMS.nba[1];return JSON.stringify({base:t[1],
    join:joinTeamStr(t[0],t[1]), dyn:Math.round(teamStrength('nba',t[0],t[1])*10)/10});})()`));
  check('joinTeamStr = 动态账面（teamStrength 同值）', r1.join === r1.dyn, JSON.stringify(r1));
  check('joinTeamStr 保留一位小数（与显示一致）', Math.abs(r1.join * 10 - Math.round(r1.join * 10)) < 1e-9, String(r1.join));

  /* ② 回退行为 */
  check('找不到的队（青训）→ fallback 原值', win.eval("joinTeamStr('山东高速青年队',4)") === 4);
  const r3 = win.eval(`(()=>{const save=S.world;S.world=null;const v=joinTeamStr('丹佛掘金',9);S.world=save;return v;})()`);
  check('world 未生成 → 回退底子（等价旧行为）', r3 === 9, String(r3));

  /* ③ setJoinStr：写入快照 + 标记 */
  const r4 = JSON.parse(win.eval(`(()=>{S._joinV2=undefined;setJoinStr('金州勇士',8);return JSON.stringify({v:S.teamStr,f:S._joinV2,
    dyn:Math.round(teamStrength('nba','金州勇士',8)*10)/10});})()`));
  check('setJoinStr 写入动态值', r4.v === r4.dyn, JSON.stringify(r4));
  check('setJoinStr 标记 _joinV2', r4.f === 1, String(r4.f));

  /* ④ 老档迁移 + 幂等 */
  const r5 = JSON.parse(win.eval(`(()=>{S.team='丹佛掘金';S.teamStr=9;S._joinV2=undefined;
    ensureState();const first=S.teamStr;ensureState();
    return JSON.stringify({first:first,second:S.teamStr,
    dyn:Math.round(teamStrength('nba','丹佛掘金',9)*10)/10});})()`));
  check('老档迁移：底子 → 动态账面', r5.first === r5.dyn, JSON.stringify(r5));
  check('迁移幂等（第二次不变）', r5.first === r5.second, JSON.stringify(r5));
  const r6 = win.eval(`(()=>{S.teamStr=7.3;S._joinV2=1;ensureState();return S.teamStr;})()`);
  check('_joinV2 已设 → 读档不漂移（保持 7.3）', r6 === 7.3, String(r6));

  /* ⑤ 产物字符串断言 */
  const cnt = (html.match(/setJoinStr\(/g) || []).length;
  check('setJoinStr 共 10 处（1 定义 + 9 调用）', cnt === 10, String(cnt));
  check('旧写法清零（fx.setStr / tt[1] / mt 直接赋值残留）',
    !/S\.teamStr=fx\.setStr|S\.teamStr=tt\?tt\[1\]|S\.teamStr=mt/.test(html), '检查残留');
  check('迁移段就位（_joinV2 一次性升级）', html.indexOf('if(!S._joinV2&&S.team&&S.teamStr!=null)') >= 0);
  check('注释就位（加盟强度快照）', html.indexOf('加盟强度快照') >= 0);
});
