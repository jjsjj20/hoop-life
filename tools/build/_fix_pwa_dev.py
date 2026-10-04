# -*- coding: utf-8 -*-
"""一次性修复：patch_pwa.py 的 CACHE 改为占位（真值由 patch_sw_cache.py 覆写）。"""
import ast

P = 'patch_pwa.py'
s = open(P, encoding='utf-8').read()

old_block = """import hashlib
# R1（v4.15.1）：SW 缓存名 = 游戏 HTML 的内容哈希（sha256 前 12 位）——
# 重建有任何变化即换缓存（老用户资产自动刷新）；完全一致的重建缓存不失效。
CACHE = 'hoop-life-' + hashlib.sha256(s.encode('utf-8')).hexdigest()[:12]"""
new_block = """# R1（v4.15.1）：SW 缓存名由 patch_sw_cache.py 按最终 HTML 的内容哈希覆写（此处仅占位）"""
assert old_block in s, 'hash block not found'
s = s.replace(old_block, new_block)

old1 = 'SW = """/* 篮球人生 Service Worker（""" + CACHE + """）'
new1 = "SW = \"\"\"/* 篮球人生 Service Worker（\"\"\" + 'hoop-life-DEV' + \"\"\"）"
assert old1 in s, 'old1 not found'
s = s.replace(old1, new1)

old2 = "const CACHE = '\"\"\" + CACHE + \"\"\"';"
new2 = "const CACHE = 'hoop-life-DEV';"
assert old2 in s, 'old2 not found'
s = s.replace(old2, new2)

ast.parse(s)
open(P, 'w', encoding='utf-8').write(s)
print('patch_pwa.py 占位化完成，语法 OK')
