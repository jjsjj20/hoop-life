/* 功能页返回：同级切换、直接返回、嵌套返回及事件控件恢复。 */
const { run } = require('./testkit');

module.exports = run('功能页返回', ({ win, doc, check, errors, key }) => {
  let desktop = true;
  win.matchMedia = query => ({ matches: desktop && query === '(min-width:900px)' });
  win.eval("renderCreate();document.getElementById('fName').value='返回测试';doCreate();allocRandom();confirmAlloc();");
  const choice = doc.querySelector('#chs .ch');
  const originalUI = win.eval('JSON.stringify(UI)');
  check('事件侧栏提供当前事件入口', !!doc.querySelector('.funcbar button[data-f="event"]'));
  check('原始事件选项有点击响应', !!choice && typeof choice.onclick === 'function');

  win.openFunc('attrs');
  check('功能页顶部提供直接返回按钮', !!doc.querySelector('#stage .func-return'));
  win.openFunc('tend');
  win.closeOvl();
  check('切换多个同级功能后一次关闭回到原事件', doc.querySelector('#chs .ch') === choice);
  check('返回后仍保留选项的点击响应', typeof doc.querySelector('#chs .ch').onclick === 'function');
  check('查看功能未重抽事件或推进剧情', win.eval('JSON.stringify(UI)') === originalUI);

  win.openFunc('attrs');
  doc.querySelector('.funcbar button[data-f="attrs"]').click();
  check('再次点击当前功能直接收起', doc.querySelector('#chs .ch') === choice);
  check('收起后当前事件高亮', doc.querySelector('.funcbar button[aria-current="page"]').dataset.f === 'event');

  win.openFunc('attrs');
  const attrs = doc.querySelector('#stage .funcpage');
  win.openOvl('<h3>属性详情</h3><input id="detailInput" value="未修改">');
  doc.getElementById('detailInput').value = '保留输入';
  win.closeOvl();
  check('嵌套详情仍能返回上一层功能页', doc.querySelector('#stage .funcpage') === attrs);
  check('返回上一层恢复正确导航高亮', doc.querySelector('.funcbar button[aria-current="page"]').dataset.f === 'attrs');
  win.openOvl('<h3>嵌套详情</h3>');
  doc.querySelector('#stage .func-return').click();
  check('嵌套详情也能一键返回原事件', doc.querySelector('#chs .ch') === choice);

  win.openFunc('attrs');
  key('Escape');
  check('Escape 可以关闭桌面功能页', doc.querySelector('#chs .ch') === choice);
  win.openFunc('attrs');
  doc.querySelector('.funcbar button[data-f="event"]').click();
  choice.click();
  check('返回后点击原选项可正常进入结果', win.eval('UI.mode') === 'result');

  const result = doc.querySelector('#stage .result');
  const details = doc.querySelector('.result-status');
  details.open = true;
  const resultState = win.eval('JSON.stringify({S,UI})');
  win.openFunc('attrs');
  doc.querySelector('#stage .func-return').click();
  check('从结果页打开功能后回到原结果', doc.querySelector('#stage .result') === result);
  check('结果页展开状态保留', doc.querySelector('.result-status').open);
  check('返回结果不重复结算或推进', win.eval('JSON.stringify({S,UI})') === resultState);
  doc.querySelector('#stage .contBtn').click();
  check('恢复后的继续按钮正常推进', win.eval('UI.mode') === 'event');

  const nextChoice = doc.querySelector('#chs .ch');
  win.openFunc('attrs');
  desktop = false;
  win.closeOvl();
  check('功能页打开后缩窄窗口仍能返回事件', doc.querySelector('#chs .ch') === nextChoice);
  win.openFunc('attrs');
  check('手机端仍使用功能弹层', doc.getElementById('ovl').classList.contains('on'));
  win.closeOvl();
  check('手机关闭弹层后事件保持可操作',
    !doc.getElementById('ovl').classList.contains('on') && doc.querySelector('#chs .ch') === nextChoice && typeof nextChoice.onclick === 'function');
  check('功能往返无运行时异常', errors.length === 0, errors.join(' | '));
});
