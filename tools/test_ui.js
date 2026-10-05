/* 移动端布局优化（v4.19）——回归钉：
 *  ① CSS 规则就位：HUD 收起态、行动栏吸底、插画压缩（仅移动端媒体查询）
 *  ② renderTop 渲染收起按钮，初始态与 localStorage 一致
 *  ③ toggleHudMin 切换 .hud.min 类并写入 localStorage（hl_hudmin） */
const { run } = require('./testkit');

module.exports = run('移动端布局', ({ win, doc, check, html }) => {
  win.eval('renderCreate();');
  win.eval("document.getElementById('fName').value='布局测试';");
  win.eval('doCreate(); allocRandom(); confirmAlloc();');
  win.eval(`
    S.league='NBA'; S.team=TEAMS.nba[0][0]; S.age=20; ensureWorld();
    UI={mode:'event',ev:null};renderGame();
  `);

  // ── ① CSS 规则 ──
  check('HUD 收起态 CSS 就位（.hud.min 隐藏阶段条与 chips）',
    html.indexOf('.hud.min .stagebar,.hud.min .chips{display:none}') >= 0);
  check('行动栏吸底 CSS 就位（仅移动端）',
    html.indexOf('.actions{position:sticky;bottom:0;z-index:7') >= 0);
  check('移动端插画压缩（128→96px）', html.indexOf('.art{height:96px') >= 0);
  check('收起按钮移动端可见、桌面隐藏',
    html.indexOf('.hudmin{display:none') >= 0 && html.indexOf('.hudmin{display:flex}') >= 0);

  // ── ② 渲染 ──
  win.eval('localStorage.removeItem(\'hl_hudmin\'); HUD_MIN=false; UI={mode:\'event\',ev:null}; renderGame();');
  const hud1 = doc.querySelector('.hud');
  check('HUD 渲染出收起按钮', !!hud1 && !!hud1.querySelector('.hudmin'));
  check('初始态未收起（无 min 类）', hud1.className.indexOf('min') < 0, hud1.className);

  // ── ③ 切换行为 ──
  win.eval('toggleHudMin();');
  const hud2 = doc.querySelector('.hud');
  const ls1 = win.eval("localStorage.getItem('hl_hudmin')");
  check('toggle 后 HUD 进入收起态（.hud.min）', hud2.className.indexOf('min') >= 0, hud2.className);
  check('收起态写入 localStorage', ls1 === '1', String(ls1));
  check('收起态按钮切换为 ▾', hud2.querySelector('.hudmin').textContent === '▾',
    hud2.querySelector('.hudmin').textContent);

  win.eval('toggleHudMin();');
  const hud3 = doc.querySelector('.hud');
  const ls2 = win.eval("localStorage.getItem('hl_hudmin')");
  check('再切换恢复展开态', hud3.className.indexOf('min') < 0, hud3.className);
  check('localStorage 同步为 0', ls2 === '0', String(ls2));

  // ── ④ 事件内容不因切换丢失 ──
  check('切换 HUD 后事件仍在（renderGame 保留 UI.ev）', !!win.eval('UI.ev'));
});
