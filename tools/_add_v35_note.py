# -*- coding: utf-8 -*-
"""在更新日志（md+html）里补记 v3.5 谱系关系（不改动被测试计数的结构）。"""
import io

NOTE_MD = """> 补记（2026-10-06）：**v3.5「视觉精修」在本项目基线内已包含**——极光氛围 / 暗角 / 水晶卡片 /
> 按钮扫光 / 选项泛光 / HUD 能力环 / 玻璃模态 / 细滚动条 / 焦点环 / reduced-motion /
> 篮球**圆形**光环（动画键名 `v35halo`）/ 主菜单存档摘要显示（含「📂 读取存档，继续生涯」）
> 均已复现并端到端验证（建档→存档→回主菜单可见）。本项目谱系自 v3.6 起，故无单独的 v3.5 条目。"""

p = '更新日志.md'
s = io.open(p, encoding='utf-8').read()
anchor = '> 当前版本：**v4.21.0** · 最后更新：2026-10-05'
assert anchor in s, 'md 锚点未找到'
if 'v3.5「视觉精修」在本项目基线内已包含' not in s:
    s = s.replace(anchor, anchor + '\n>\n' + NOTE_MD, 1)
    io.open(p, 'w', encoding='utf-8').write(s)
print('md 补记已加')

NOTE_HTML = ('<div class="mini" style="margin:8px 0 0;opacity:.75">补记（2026-10-06）：本页谱系自 v3.6 起——'
             '<b>v3.5「视觉精修」的全部条目（极光 / 水晶卡片 / 按钮扫光 / 圆形篮球光环 / 主菜单存档摘要）'
             '在本项目基线内已包含</b>，并已端到端验证（建档→存档→回主菜单可见存档摘要与「📂 读取存档」）。</div>')

p = '更新日志.html'
s = io.open(p, encoding='utf-8').read()
mark = '资源外置 · 105 张 WebP</span></div>'
i = s.find(mark)
assert i > 0, 'html 锚点未找到'
j = i + len(mark)
if 'v3.5「视觉精修」的全部条目' not in s:
    s = s[:j] + NOTE_HTML + s[j:]
    io.open(p, 'w', encoding='utf-8').write(s)
print('html 补记已加')
