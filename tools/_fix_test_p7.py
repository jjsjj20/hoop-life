# -*- coding: utf-8 -*-
"""把 test_p7.js 的行动栏断言升级为「减负 + ☰ 更多菜单」版本。"""
import io

P = 'test_p7.js'
ls = io.open(P, encoding='utf-8').read().split('\n')

# 定位旧的行动栏断言块（以注释行开头）
start = None
for i, l in enumerate(ls):
    if l.strip().startswith('// ── 行动栏'):
        start = i
        break
if start is None:
    raise SystemExit('!! 找不到行动栏断言块')
# 块 = 注释行 + 2 行（renderGame + 旧断言）
new_block = [
    '  // ── 行动栏减负（v4.18）：内联 ≤6 个 + ☰ 更多菜单承载次要功能 ──',
    '  win.eval("UI={mode:\'event\',ev:null};renderGame();");',
    "  const appHtml = doc.getElementById('app').innerHTML;",
    '  const actM = appHtml.match(/<div class="actions">([\\s\\S]*?)<\\/div>/);',
    '  const inlineN = actM ? (actM[1].match(/<button/g) || []).length : 99;',
    "  check('行动栏内联按钮 ≤ 6 个（原 15）', inlineN <= 6, '实际 ' + inlineN + ' 个');",
    "  check('保留高频按钮：阵容/排名/AI/存档/更多',",
    "    ['showRoster()', 'AI.openPanel()', 'saveNow()', 'openMore()'].every(fn => appHtml.indexOf(fn) >= 0));",
    '  win.eval("openMore()");',
    '  const moreHtml = doc.body.innerHTML;',
    "  check('☰ 更多 菜单含签位/财务/成就/档案',",
    "    ['showPickAssets()', 'showMoney()', 'showCodex()', 'showArchive()'].every(fn => moreHtml.indexOf(fn) >= 0));",
    "  check('☰ 更多 菜单含音效/导出/导入/结束生涯',",
    "    ['toggleSfx()', 'exportSave()', 'openImport()', 'endNow()'].every(fn => moreHtml.indexOf(fn) >= 0))",
]
# 注意最后一行不带分号（原块末行是 check(...);，我们保留分号）——修正为带分号
new_block[-1] = new_block[-1] + ';'

ls[start:start + 3] = new_block
io.open(P, 'w', encoding='utf-8').write('\n'.join(ls))
print('test_p7 行动栏断言已升级')
