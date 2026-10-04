# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 18：SW 缓存名 = 最终 HTML 的内容哈希（R1 的收口步骤）

必须放在所有会修改 HTML 的步骤之后：读取**最终** HTML，计算 sha256（前 12 位），
覆写 sw.js 的 CACHE 常量。此后无论新增多少构建步骤，SW 缓存名永远与产物一致——
重建有任何变化即换缓存（老用户资产自动刷新），完全一致的重建缓存不失效。
patch_pwa.py 生成的 sw.js 里 CACHE='hoop-life-DEV' 只是占位，由本步骤覆写。
"""
import hashlib
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
HTML = os.environ.get('GAME_HTML') or os.path.join(BASE, '..', 'output', '篮球人生.html')
SW = os.path.join(os.path.dirname(HTML), 'sw.js')

html = open(HTML, encoding='utf-8').read()
cache = 'hoop-life-' + hashlib.sha256(html.encode('utf-8')).hexdigest()[:12]

if not os.path.exists(SW):
    raise SystemExit('!! 找不到 sw.js（patch_pwa 应先生成）')
sw = open(SW, encoding='utf-8').read()
pat = re.compile(r"const CACHE = 'hoop-life-[0-9a-zA-Z.]+';")
if len(pat.findall(sw)) != 1:
    raise SystemExit('!! sw.js 的 CACHE 行匹配 %d 次（期望 1）' % len(pat.findall(sw)))
sw = pat.sub("const CACHE = '" + cache + "';", sw)
open(SW, 'w', encoding='utf-8', newline='\n').write(sw)
print('SW 缓存名已对齐最终产物：' + cache)
