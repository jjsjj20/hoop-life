# -*- coding: utf-8 -*-
"""给 test_ui.js 追加「结果页剧情折叠」（v4.19.2）断言。"""
import io

P = 'test_ui.js'
s = io.open(P, encoding='utf-8').read()

anchor = "  // ── ④ 事件内容不因切换丢失 ──"
assert anchor in s, 'anchor not found'

block = '''  // ── ⑥ 结果页剧情折叠（v4.19.2）──
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

'''
s = s.replace(anchor, block + anchor, 1)
io.open(P, 'w', encoding='utf-8').write(s)
print('test_ui 已追加剧情折叠断言')
