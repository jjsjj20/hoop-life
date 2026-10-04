# -*- coding: utf-8 -*-
"""一次性修复：把 patch_content_p5.py 残缺的 spring sub1 补成正确的双参调用。"""
import ast

P = 'patch_content_p5.py'
lines = open(P, encoding='utf-8').read().split('\n')

PILLAR = "    ch('公开回击那些嘲讽者',{stability:-1,ts:-1,clutch:1},'他赢了口水战，也给自己加了一份不必要的压力。')"
start = None
for i, ln in enumerate(lines):
    if ln.startswith('sub1("""' + PILLAR[:20]):
        start = i
        break
if start is None:
    raise SystemExit('!! 找不到 spring sub1 起点')

repl = [
    'sub1("""' + PILLAR,
    '  ])',
    '];""",',
    '"""' + PILLAR,
    '  ]),%s',
    '];""" % SPRING, \'春池 +12\')',
]
lines[start:start + 3] = repl

out = '\n'.join(lines)
ast.parse(out)   # 语法必须通过
open(P, 'w', encoding='utf-8').write(out)
print('spring sub1 已修复，语法 OK')
