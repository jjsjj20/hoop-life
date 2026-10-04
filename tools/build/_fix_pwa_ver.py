# -*- coding: utf-8 -*-
"""一次性修复：patch_pwa.py 的 SW 拼接行 VER → CACHE（patch 内已算好的内容哈希变量）。"""
import ast

P = 'patch_pwa.py'
s = open(P, encoding='utf-8').read()

# 行 80：SW 三引号串头部的版本拼接 → 改用内容哈希变量
old1 = 'SW = """/* 篮球人生 Service Worker（""" + VER + """）'
new1 = 'SW = """/* 篮球人生 Service Worker（""" + CACHE + """）'
# 行 84：SW 串内部的 CACHE 常量行 → 拼接 patch 内的 CACHE 变量
old2 = "const CACHE = 'hoop-life-\"\"\" + VER + \"\"\"';"
new2 = "const CACHE = '\"\"\" + CACHE + \"\"\"';"

assert old1 in s, 'old1 not found'
s = s.replace(old1, new1)
assert old2 in s, 'old2 not found'
s = s.replace(old2, new2)

ast.parse(s)
open(P, 'w', encoding='utf-8').write(s)
print('patch_pwa.py 已修复，语法 OK')
