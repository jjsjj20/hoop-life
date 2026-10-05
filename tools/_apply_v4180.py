# -*- coding: utf-8 -*-
"""写 v4.18.0 更新日志（md+html）+ 测试常量 + 计划勾选。"""
import io

# ── 更新日志.md ──
p = '更新日志.md'
s = io.open(p, encoding='utf-8').read()
s = s.replace('> 当前版本：**v4.17.0** · 最后更新：2026-10-04',
              '> 当前版本：**v4.18.0** · 最后更新：2026-10-05')
s = s.replace('| **v4.17.0**',
              '| **v4.18.0** | 行动栏减负：15 个按钮收敛为 5 + ☰ 更多菜单（游玩反馈第一条落地） | `e363c25` | +668 |\n| **v4.17.0**', 1)
entry = '''
---

## ☰ v4.18.0 · 行动栏减负：15 个按钮收敛为 5 + ☰ 更多菜单

**提交**：`e363c25` · **文件**：577,654 字符（+668，相对 v4.17.0 的 576,986）

游玩反馈第一条「按钮太多了」的落地。行动栏经 13 个版本叠加到 15 个按钮
（阵容/排名/签位/对阵图/财务/倾向/档案/成就/AI/新闻/音效/存档/导出/导入/结束），
手机上要滚两屏。

### 整合方案
- **行内保留 5 个**（高频与安全项）：👥 阵容 · 📊 排名 · 🤖 AI · 💾 存档 · ☰ 更多；
- **☰ 更多分组覆盖层**（10 项按用途归组）：
  - 数据：📋 签位 · 🏆 对阵图（条件出现）· 💼 财务 · 🏆 成就 · 📋 档案
  - 设置与工具：🧭 倾向 · 📰 新闻 · 🔊 音效 · 📤 导出存档 · 📥 导入存档
  - 生涯：🏁 提前结束生涯
- `toggleSfx` 的提示文案同步改指「☰ 更多 → 🔊 音效」。

### 验证记录
- 验证套件 **19/19 项 · 483/483 断言**全部通过（`p7` 断言升级为
  「内联 ≤6 个 + 菜单承载次要功能」，13→16 断言）；
- 重建（现 21 步）与仓库成品**逐字节一致**。

---

## 🏫 v4.17.0 · R2 青训体验补强：40 条青训事件（池 11→21）'''
s = s.replace('\n---\n\n## 🏫 v4.17.0 · R2 青训体验补强：40 条青训事件（池 11→21）', entry, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('md done')

# ── 更新日志.html ──
p = '更新日志.html'
s = io.open(p, encoding='utf-8').read()
s = s.replace('<span class="badge">当前版本 <b>v4.17.0</b></span><span class="badge">文件 <b>576,986</b> 字符</span><span class="badge">更新 <b>31</b> 个版本</span>',
              '<span class="badge">当前版本 <b>v4.18.0</b></span><span class="badge">文件 <b>577,654</b> 字符</span><span class="badge">更新 <b>32</b> 个版本</span>')
s = s.replace('<nav class="toc"><a href="#v4170">v4.17.0</a>',
              '<nav class="toc"><a href="#v4180">v4.18.0</a><a href="#v4170">v4.17.0</a>')
s = s.replace('<tr><td><b>v4.17.0</b></td>',
              '<tr><td><b>v4.18.0</b></td><td>行动栏减负：15 个按钮收敛为 5 + ☰ 更多菜单（游玩反馈第一条落地）</td><td><code>e363c25</code></td><td>+668</td></tr>\n<tr><td><b>v4.17.0</b></td>', 1)
entry = '''<h2 id="v4180">☰ v4.18.0 · 行动栏减负：15 个按钮收敛为 5 + ☰ 更多菜单 <span class="sha">e363c25</span></h2>
<div class="card">
<p>游玩反馈第一条「按钮太多了」的落地。行动栏经 13 个版本叠加到 15 个按钮（阵容/排名/签位/对阵图/财务/倾向/档案/成就/AI/新闻/音效/存档/导出/导入/结束），手机上要滚两屏。</p>
<h3>整合方案</h3>
<ul>
<li><b>行内保留 5 个</b>（高频与安全项）：👥 阵容 · 📊 排名 · 🤖 AI · 💾 存档 · ☰ 更多；</li>
<li><b>☰ 更多分组覆盖层</b>（10 项按用途归组）：数据（📋 签位 · 🏆 对阵图 · 💼 财务 · 🏆 成就 · 📋 档案）· 设置与工具（🧭 倾向 · 📰 新闻 · 🔊 音效 · 📤 导出存档 · 📥 导入存档）· 生涯（🏁 提前结束生涯）；</li>
<li><code>toggleSfx</code> 的提示文案同步改指「☰ 更多 → 🔊 音效」。</li>
</ul>
<h3>验证记录</h3>
<ul>
<li>验证套件 <b>19/19 项 · 483/483 断言</b>全部通过（<code>p7</code> 断言升级为「内联 ≤6 个 + 菜单承载次要功能」，13→16 断言）；</li>
<li>重建（现 21 步）与仓库成品<b>逐字节一致</b>。</li>
</ul>
</div>
<h2 id="v4170">'''
s = s.replace('<h2 id="v4170">', entry, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('html done')

# ── 测试常量 ──
p = 'tools/test_changelog_page.js'
s = io.open(p, encoding='utf-8').read()
s = s.replace('secs.length === 31', 'secs.length === 32')
s = s.replace("kOf('v4.17.0') === 'play', kOf('v4.17.0'));",
              "kOf('v4.17.0') === 'play', kOf('v4.17.0'));\n  check('v4.18.0（UI 减负）→ 工程', kOf('v4.18.0') === 'eng', kOf('v4.18.0'));", 1)
s = s.replace("/v4\\.17\\.0/.test(h.querySelector('.vpill').textContent)",
              "/v4\\.18\\.0/.test(h.querySelector('.vpill').textContent)")
s = s.replace("vt.indexOf('v4.17.0') < 0", "vt.indexOf('v4.18.0') < 0")
s = s.replace('chips.length === 32', 'chips.length === 33')
s = s.replace('verChips.length === 31', 'verChips.length === 32')
s = s.replace('collapsed.length === 31 - 5', 'collapsed.length === 32 - 5')
s = s.replace("'v4.17.0', 'v4.16.0'", "'v4.18.0', 'v4.17.0', 'v4.16.0'")
s = s.replace('卡片数量未变（33 个）', '卡片数量未变（34 个）')
s = s.replace(".card').length === 33", ".card').length === 34")
s = s.replace('目录芯片被搬进工具条（31 版 + 附录）', '目录芯片被搬进工具条（32 版 + 附录）')
io.open(p, 'w', encoding='utf-8').write(s)
print('constants done')
