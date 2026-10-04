# -*- coding: utf-8 -*-
"""通用修复：规范化 win.eval(...) 行的结尾括号。
错误形态：TEMPLATE 多了一个右括号 + 反引号后少了一个右括号（`)）； 正确：`))); """
import sys, glob, io

for p in sys.argv[1:] or glob.glob('test_*.js'):
    lines = io.open(p, encoding='utf-8').read().split('\n')
    fixed = 0
    for i, ln in enumerate(lines):
        if ln.endswith('`);') and '})()' in ln:
            body = ln[:-3]                       # 去掉 反引号 + );
            while body.endswith(')))'):          # 折叠多余右括号到恰好 2 个
                body = body[:-1]
            lines[i] = body + '`));'
            fixed += 1
    if fixed:
        io.open(p, 'w', encoding='utf-8').write('\n'.join(lines))
    print(p, 'fixed', fixed)
