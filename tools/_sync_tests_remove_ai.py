# -*- coding: utf-8 -*-
"""移除 AI 后同步测试：删 test_ai.js 及生成器；清掉 test_robustness / test_pwa_card / test_p7 里的 AI 依赖。"""
import io
import os

# ① 删除 AI 测试与生成器
for f in ('test_ai.js', '_gen_ai.py', '_ext_test_ai.py', '_ext_test_ai2.py', '_ext_test_ai3.py'):
    if os.path.exists(f):
        os.remove(f)
        print('已删除', f)

# ② test_robustness.js：整块移除 AI 面板/密钥断言
P = 'test_robustness.js'
ls = io.open(P, encoding='utf-8').read().split('\n')
start = next((i for i, l in enumerate(ls) if '第 6 条' in l), None)
assert start is not None, 'robustness: 找不到第 6 条'
# 找到该块结束：'清除后输入框被清空' 那一行
end = next(i for i, l in enumerate(ls) if '清除后输入框被清空' in l)
del ls[start:end + 1]
io.open(P, 'w', encoding='utf-8').write('\n'.join(ls))
print('test_robustness：已移除 AI 块（%d 行）' % (end - start + 1))

# ③ test_pwa_card.js：去掉 AI 离线断言，并修头部注释
P = 'test_pwa_card.js'
s = io.open(P, encoding='utf-8').read()
lines = [l for l in s.split('\n') if 'AI 离线明示降级提示就位' not in l]
s = '\n'.join(lines)
s = s.replace('注册带协议守卫、AI 离线明示降级 */', '注册带协议守卫 */')
s = s.replace('// ── ④ PWA：manifest / sw / 图标 / 注册守卫 / AI 离线降级 ──', '// ── ④ PWA：manifest / sw / 图标 / 注册守卫 ──')
io.open(P, 'w', encoding='utf-8').write(s)
print('test_pwa_card：已移除 AI 离线断言')

# ④ test_p7.js：行动栏必需按钮里去掉 AI
P = 'test_p7.js'
s = io.open(P, encoding='utf-8').read()
old = "    ['showRoster()', 'AI.openPanel()', 'saveNow()', 'openMore()'].every(fn => appHtml.indexOf(fn) >= 0));"
new = "    ['showRoster()', 'saveNow()', 'openMore()'].every(fn => appHtml.indexOf(fn) >= 0));"
assert old in s, 'p7: 找不到行动栏断言'
s = s.replace(old, new)
s = s.replace("check('保留高频按钮：阵容/排名/AI/存档/更多',", "check('保留高频按钮：阵容/排名/存档/更多',")
io.open(P, 'w', encoding='utf-8').write(s)
print('test_p7：已更新行动栏断言')
