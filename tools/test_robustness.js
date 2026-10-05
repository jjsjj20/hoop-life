/* 鲁棒性 —— 脚手架见 ./testkit.js */
const path = require('path');
const { run } = require('./testkit');

module.exports = run('鲁棒性', ({ win, doc, check, errors, consoleErrors, warns, html, key, click }) => {
  // ── 第 5 条 ─────────────────────────────────────────────
  check('初始没有异常记录', win.eval('CRASH_LOG.length') === 0);
  check('CRASH_LOG 上限 20', win.eval('CRASH_MAX') === 20);

  // 计数 toast，验证"限流"
  win.eval('window.__toastN=0; window.__origToast=toast; toast=function(){window.__toastN++; return window.__origToast.apply(null,arguments);};');

  const fire = (msg) => win.dispatchEvent(new win.ErrorEvent('error', {
    message: msg, filename: 'game.html', lineno: 10, colno: 5, error: new Error(msg),
  }));

  fire('boom-A');
  let log = win.eval('JSON.stringify(CRASH_LOG)');
  check('脚本异常被记录', win.eval('CRASH_LOG.length') === 1, log);
  check('记录了来源与消息', /脚本异常/.test(log) && /boom-A/.test(log), log);
  check('控制台打了 [崩溃] 日志', consoleErrors.some(x => /\[崩溃\]/.test(x)), consoleErrors.slice(0, 2).join(' | '));
  check('给了玩家一次提示', win.eval('window.__toastN') === 1, String(win.eval('window.__toastN')));
  const firstToastAt = win.eval('_crashToastAt');

  fire('boom-A');
  fire('boom-A');
  check('同一条错误合并计数不刷屏', win.eval('CRASH_LOG.length') === 1 && win.eval('CRASH_LOG[0].n') === 3,
        win.eval('JSON.stringify(CRASH_LOG)'));
  check('玩家提示做了限流（30 秒内不重复）', win.eval('window.__toastN') === 1 && win.eval('_crashToastAt') === firstToastAt,
        'toast=' + win.eval('window.__toastN'));

  fire('boom-B');
  check('不同错误各自成条', win.eval('CRASH_LOG.length') === 2);

  // unhandledrejection
  const rej = new win.Event('unhandledrejection');
  rej.reason = new Error('async-boom');
  win.dispatchEvent(rej);
  log = win.eval('JSON.stringify(CRASH_LOG)');
  check('未处理的 Promise 也被记录', /未处理的 Promise/.test(log) && /async-boom/.test(log), log);

  // 资源加载失败不该被当成代码崩溃
  const before = win.eval('CRASH_LOG.length');
  const img = doc.createElement('img');
  const rerr = new win.Event('error');
  Object.defineProperty(rerr, 'target', { value: img });
  win.dispatchEvent(rerr);
  check('资源加载失败不计入崩溃日志', win.eval('CRASH_LOG.length') === before);

  // 档案面板里能看到运行日志
  win.eval('renderCreate();');
  doc.querySelector('#fName').value = '测试';
  win.eval('doCreate(); allocRandom(); confirmAlloc();');
  let archErr = null;
  try { win.eval('showArchive();'); } catch (e) { archErr = e; }
  const ovl = doc.getElementById('ovlBody').innerHTML;
  check('档案面板能打开', !archErr, archErr && archErr.message);
  check('档案面板有「运行日志」一节', /运行日志/.test(ovl));
  check('运行日志列出了具体异常', /脚本异常/.test(ovl) && /async-boom/.test(ovl));


  // ── 结果 ───────────────────────────────────────────────
}, { ready: 1200 });
