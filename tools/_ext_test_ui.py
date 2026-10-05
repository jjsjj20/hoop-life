# -*- coding: utf-8 -*-
"""给 test_ui.js 追加「结果页继续吸底」（v4.19.1）断言。"""
import io

P = 'test_ui.js'
s = io.open(P, encoding='utf-8').read()

anchor = "  // ── ④ 事件内容不因切换丢失 ──"
assert anchor in s, 'anchor not found'

block = '''  // ── ⑤ 结果页「继续」吸底（v4.19.1）──
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

'''
s = s.replace(anchor, block + anchor, 1)
io.open(P, 'w', encoding='utf-8').write(s)
print('test_ui 已追加继续吸底断言')
