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

  // ── ⑤ 结果页「继续」吸底（v4.19.1）──
  check('结果页原按钮带 .contBtn 类', html.indexOf('class="btn contBtn" onclick="advance()"') >= 0);
  check('桌面隐藏吸底继续按钮（.contAct 基础态 display:none）', html.indexOf('.contAct{display:none}') >= 0);
  check('移动端隐藏原按钮、显示橙色吸底继续',
    html.indexOf('.contBtn{display:none}') >= 0 &&
    html.indexOf('.contAct{display:block;background:linear-gradient(180deg,#f97316,#ea580c)') >= 0);
  win.eval("UI={mode:'event',ev:null};renderGame();");
  const actEv = doc.querySelector('.actions');
  check('事件模式下行动栏无「继续」', !actEv.querySelector('.contAct'));
  win.eval('choose(0)');
  check('选择后进入结果模式', win.eval('UI.mode') === 'result', String(win.eval('UI.mode')));
  const actRes = doc.querySelector('.actions');
  check('结果模式下行动栏出现吸底「继续」',
    !!actRes.querySelector('.contAct') &&
    actRes.querySelector('.contAct').getAttribute('onclick') === 'advance()');

  // ── ⑥ 结果页剧情折叠（v4.19.2）──
  check('结果页剧情块带 .sceneFold 且按钮就位',
    html.indexOf('class="scene sceneFold" id="resScene"') >= 0 &&
    html.indexOf('id="resFoldBtn"') >= 0);
  check('桌面隐藏折叠开关（.foldBtn 基础态）', html.indexOf('.foldBtn{display:none}') >= 0);
  check('移动端默认收起剧情（:not(.show)）', html.indexOf('.sceneFold:not(.show){display:none}') >= 0);
  win.eval("UI={mode:'event',ev:null};renderGame();");
  win.eval('choose(0)');
  const scEl = doc.getElementById('resScene');
  check('结果页渲染出可折叠剧情块', !!scEl && scEl.classList.contains('sceneFold'));
  check('默认未展开（无 .show）', scEl && !scEl.classList.contains('show'));
  win.eval('toggleSceneFold()');
  check('点开关后展开（.show）且文案变「收起剧情」',
    doc.getElementById('resScene').classList.contains('show') &&
    doc.getElementById('resFoldBtn').textContent.indexOf('收起剧情') >= 0,
    doc.getElementById('resFoldBtn').textContent);
  win.eval('toggleSceneFold()');
  check('再点一次收起、文案复位',
    !doc.getElementById('resScene').classList.contains('show') &&
    doc.getElementById('resFoldBtn').textContent.indexOf('展开剧情') >= 0);

  // ── ④ 事件内容不因切换丢失 ──
  check('切换 HUD 后事件仍在（renderGame 保留 UI.ev）', !!win.eval('UI.ev'));
});
