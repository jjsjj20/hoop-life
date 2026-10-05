# -*- coding: utf-8 -*-
"""修正 patch_ai_only.py：把 AI.san 块里的三条正则改为无反斜杠版本（按行替换，绕开转义）。"""
import io

P = 'patch_ai_only.py'
lines = io.open(P, encoding='utf-8').read().split('\n')

NEW = {
    '字数括注': " t=t.replace(/[（(](?:约|共|全文|字数)? ?[0-9]{1,4} ?字[)）]/g,'');",
    '整体包裹的引号': " out=out.replace(/^[“\"「『]([^]*)[”\"」』]$/,function(m,a){return a;});",
    '残留行首标签': " out=out.replace(/^(?:草稿|正文|说明|注|备注|检查|字数|要求)[：:] */g,'');",
}
hits = 0
for i, ln in enumerate(lines):
    for key, newline in NEW.items():
        if key in ln and ln.strip().startswith(('t=t.replace', 'out=out.replace')):
            lines[i] = newline
            hits += 1
io.open(P, 'w', encoding='utf-8').write('\n'.join(lines))
print('按行替换完成，命中', hits, '处')
