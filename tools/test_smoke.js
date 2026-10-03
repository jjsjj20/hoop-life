/* 冒烟 —— 脚手架见 ./testkit.js */
const path = require('path');
const { run } = require('./testkit');

module.exports = run('冒烟', ({ win, doc, check, errors, consoleErrors, warns, html, key, click }) => {
  // ══ 1. 启动 ══════════════════════════════════════════════
  check('脚本无未捕获异常', errors.length === 0, errors.slice(0, 3).join(' | '));
  check('主菜单已渲染', /开始游戏/.test(doc.querySelector('#app').innerHTML));
  check('主菜单有「导入」入口（无存档态）', /从这里导入/.test(doc.querySelector('#app').innerHTML));
  check('队徽表指向外链', /^assets\/crest\/001\.webp$/.test(String(win.eval('crestData("辽宁本钢")'))));
  check('成就图标指向外链', /^assets\/ach\/ball\.webp$/.test(String(win.eval('ACH_ICONS.ball'))));
  check('场景插图指向外链', /^assets\/art\/arena\.webp$/.test(String(win.eval('ART_IMG.arena'))));

  // ══ 2. 真实流程：建档 → 事件 → 键盘选 → 结算 → 继续 ══════
  let flowErr = null;
  try {
    win.eval('renderCreate();');
    doc.querySelector('#fName').value = '测试球员';
    win.eval('doCreate();');
    win.eval('allocRandom();');
    win.eval('confirmAlloc();');
  } catch (e) { flowErr = e; }
  check('建档 → 开局流程无异常', !flowErr, flowErr && flowErr.message);

  const st1 = doc.getElementById('stage');
  const nCh = st1 ? st1.querySelectorAll('.ch').length : 0;
  check('开局后进入事件页（有选项）', nCh > 0, '选项数=' + nCh);
  check('事件页带键盘提示', /数字键 1-9/.test(st1 ? st1.innerHTML : ''));
  check('事件页插图走外链', !/data:image/.test(st1 ? st1.innerHTML : '') && /assets\/art\//.test(st1 ? st1.innerHTML : ''));

  const beforeHtml = st1.innerHTML;
  key('1');
  const afterHtml = doc.getElementById('stage').innerHTML;
  check('键盘 1 触发结算页', afterHtml !== beforeHtml && /继续 ▶/.test(afterHtml));
  check('结算页有「空格继续」提示', /空格 \/ Enter 也可以继续/.test(afterHtml));
  check('结算页无内联图片', !/data:image/.test(afterHtml));

  const modeBefore = win.eval('UI.mode');
  key(' ');
  const modeAfter = win.eval('UI.mode');
  const okAfter = modeAfter !== 'result' || doc.getElementById('stage').innerHTML !== afterHtml;
  check('空格继续能推进剧情', okAfter, modeBefore + ' -> ' + modeAfter);

  // ══ 3. 键盘分支 ══════════════════════════════════════════
  const app = doc.querySelector('#app');
  app.innerHTML = '<div id="stage"><div id="chs"></div><button class="btn" onclick="advance()">继续 ▶</button></div>';
  const chs = doc.getElementById('chs');
  const clicked = [];
  for (let i = 0; i < 3; i++) {
    const b = doc.createElement('button');
    b.className = 'ch';
    b.innerHTML = '<span class="idx">' + (i + 1) + '</span><span class="ctext">选项' + (i + 1) + '</span>';
    b.onclick = () => clicked.push(i);
    chs.appendChild(b);
  }
  key('2');
  check('数字键 2 选中第二个选项', clicked.length === 1 && clicked[0] === 1, JSON.stringify(clicked));
  key(' ');
  check('无高亮时空格不替玩家拍板', clicked.length === 1, JSON.stringify(clicked));
  key('ArrowDown');
  check('↓ 高亮到第一项', chs.children[0].classList.contains('kbsel'));
  key('ArrowDown');
  check('再按 ↓ 高亮到第二项', chs.children[1].classList.contains('kbsel') && !chs.children[0].classList.contains('kbsel'));
  key('Enter');
  check('Enter 确认高亮项', clicked.length === 2 && clicked[1] === 1, JSON.stringify(clicked));
  key('Escape');
  check('Esc 清掉高亮', !chs.children[1].classList.contains('kbsel'));

  chs.innerHTML = '';
  let advanced = 0;
  doc.querySelector('#stage button.btn').onclick = () => { advanced++; };
  key(' ');
  key('Enter');
  check('结果页空格 / Enter 触发「继续」', advanced === 2, String(advanced));

  const ta = doc.createElement('textarea');
  doc.querySelector('#stage').appendChild(ta);
  ta.focus();
  const before = advanced;
  ta.dispatchEvent(new win.KeyboardEvent('keydown', { key: ' ', bubbles: true, cancelable: true }));
  check('输入框内空格不触发继续', advanced === before);

  // 弹窗打开时不抢键
  win.eval("openOvl('<b>x</b>','mid')");
  key('1');
  check('弹窗打开时数字键不选选项', clicked.length === 2, JSON.stringify(clicked));
  key('Escape');
  check('Esc 能关掉弹窗', !doc.getElementById('ovl').classList.contains('on'));

  // ══ 4. 存档导出 / 导入 ═══════════════════════════════════
  const SAVE_KEY = win.eval('CFG.SAVE_KEY');
  win.eval('saveNow()');
  check('存档已写入 localStorage', !!win.localStorage.getItem(SAVE_KEY));

  const dl = { name: null, clicked: 0 };
  const origClick = win.HTMLAnchorElement.prototype.click;
  win.HTMLAnchorElement.prototype.click = function () { dl.clicked++; dl.name = this.download; };
  let threw = null;
  try { win.exportSave(); } catch (e) { threw = e; }
  win.HTMLAnchorElement.prototype.click = origClick;
  check('导出不抛异常', !threw, threw && threw.message);
  check('导出触发下载且文件名合理', dl.clicked === 1 && /^hooplife-存档-.*\.json$/.test(dl.name || ''), String(dl.name));

  // 导入：走文本通道，写入后再读回
  const exported = win.localStorage.getItem(SAVE_KEY);
  win.localStorage.removeItem(SAVE_KEY);
  let threw2 = null;
  try { win.applySaveText(exported); } catch (e) { threw2 = e; }
  check('导入不抛异常', !threw2, threw2 && threw2.message);
  const back = win.localStorage.getItem(SAVE_KEY);
  check('导入把存档写回了 localStorage', !!back && /测试球员/.test(back));
  check('导入后能继续生涯', /测试球员/.test(win.eval('S.name')));

  // 拒绝非本游戏的文本
  win.localStorage.removeItem(SAVE_KEY);
  win.applySaveText('{"hello":"world"}');
  check('非法内容不会写入存档', win.localStorage.getItem(SAVE_KEY) === null);

  // 更新版本的存档要拦一下（confirm 返回 false 时不写）
  win.localStorage.removeItem(SAVE_KEY);
  const oldConfirm = win.confirm;
  win.confirm = () => false;
  win.applySaveText(JSON.stringify({ v: 999, S: { name: '未来的存档' } }));
  win.confirm = oldConfirm;
  check('更高版本的存档在取消时不写入', win.localStorage.getItem(SAVE_KEY) === null);

  // ══ 结果 ═════════════════════════════════════════════════
}, { ready: 1200 });
