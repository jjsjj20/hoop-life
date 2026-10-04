# -*- coding: utf-8 -*-
"""一次性修复：把 patch_pwa.py 的 CACHE 哈希计算移到全部 HTML 修改之后。"""
import ast

P = 'patch_pwa.py'
s = open(P, encoding='utf-8').read()

block_start = s.index('import hashlib')
block_end = s.index("hexdigest()[:12]", block_start) + len("hexdigest()[:12]")
# 块尾可能还带换行
while s[block_end] == '\n':
    block_end += 1
    break
block = s[block_start:block_end]
s = s[:block_start] + s[block_end:]

anchor = 'SW = """/* 篮球人生 Service Worker（'
ins = s.index(anchor)
s = s[:ins] + block + '\n' + s[ins:]

ast.parse(s)
open(P, 'w', encoding='utf-8').write(s)
print('CACHE 计算已移到修改之后，语法 OK')
