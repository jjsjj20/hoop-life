# -*- coding: utf-8 -*-
"""给 patch_ai_fix.py 追加「长文清洗上限」修正（报纸等多段输出不再被 700 字截断）。"""
import io

P = 'patch_ai_fix.py'
s = io.open(P, encoding='utf-8').read()

old = """AI.ask(b.sys,b.user,{mt:900}).then(function(t){
  AI.busy=false;
  const txt=AI.san(t);"""
new = """AI.ask(b.sys,b.user,{mt:900}).then(function(t){
  AI.busy=false;
  const txt=AI.san(t,1200);   /* v4.20.2：多段长文（报纸）不再被 700 字截断 */"""

block = '''
# ═══════════ ⑥ 长文清洗上限（报纸等多段输出）═══════════
sub1("""%s""", """%s""", '报纸清洗上限')

open(HTML, ''' % (old, new)

s = s.replace('\nopen(HTML, ', '\n' + block, 1)
io.open(P, 'w', encoding='utf-8').write(s)
print('补丁已追加长文清洗上限')
