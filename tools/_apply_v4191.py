# -*- coding: utf-8 -*-
"""写 v4.19.1 更新日志（md+html）+ 测试常量。"""
import io

# ── 更新日志.md ──
p = '更新日志.md'
s = io.open(p, encoding='utf-8').read()
s = s.replace('> 当前版本：**v4.19.0** · 最后更新：2026-10-05',
              '> 当前版本：**v4.19.1** · 最后更新：2026-10-05')
s = s.replace('| **v4.19.0**',
              '| **v4.19.1** | 修复：移动端结果页「继续」吸底（选完直接点，不用下滑） | `09b1e55` | +549 |\n| **v4.19.0**', 1)
entry = '''
---

## 📱 v4.19.1 · 修复：移动端结果页「继续」吸底

**提交**：`09b1e55` · **文件**：579,642 字符（+549，相对 v4.19.0 的 579,093）

游玩反馈第三条：「手机上选完后还要下滑点继续」。结果页的「继续 ▶」按钮
落在 `#stage` 内容流末尾——选项结算信息一多，就得下滑才够得着。

### 修复（桌面不变，仅移动端）
- 结果页原按钮加 `.contBtn` 类；`renderResult` 末尾把「继续 ▶」**注入吸底行动栏**（`.contAct`）；
- 移动端：隐藏原按钮，行动栏显示橙色主行动「继续 ▶」——选完直接点，无需下滑；
- 桌面：`.contAct` 默认隐藏，一切照旧。

### 实现要点（首版踩坑已修）
`choose()` 结算后**直接调用 `renderResult`、不重渲整页**——因此行动栏按钮必须用
DOM 注入而非在 `renderGame` 里做条件渲染（首版走的后者，测试立刻抓到按钮不出现）。

### 版本号规则变更（2026-10-05 起）
小更新 / 修复**只加 0.0.1**（本版即首个补丁号版本）；新功能、新玩法、
机制级改动才用次版本号。已写入开发计划「固定交付物」第 3 条。

### 验证记录
- 验证套件 **20/20 项 · 505/505 断言**全部通过（`ui` 追加 6 断言，
  含 `choose(0)` → 结果模式 → 吸底继续 的端到端验证）；
- 重建（现 23 步）与仓库成品**逐字节一致**。

---

## 📱 v4.19.0 · 移动端布局重构：HUD 可收起 · 行动栏吸底 · 插画压缩'''
s = s.replace('\n---\n\n## 📱 v4.19.0 · 移动端布局重构：HUD 可收起 · 行动栏吸底 · 插画压缩', entry, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('md done')

# ── 更新日志.html ──
p = '更新日志.html'
s = io.open(p, encoding='utf-8').read()
s = s.replace('<span class="badge">当前版本 <b>v4.19.0</b></span><span class="badge">文件 <b>579,093</b> 字符</span><span class="badge">更新 <b>33</b> 个版本</span>',
              '<span class="badge">当前版本 <b>v4.19.1</b></span><span class="badge">文件 <b>579,642</b> 字符</span><span class="badge">更新 <b>34</b> 个版本</span>')
s = s.replace('<nav class="toc"><a href="#v4190">v4.19.0</a>',
              '<nav class="toc"><a href="#v4191">v4.19.1</a><a href="#v4190">v4.19.0</a>')
s = s.replace('<tr><td><b>v4.19.0</b></td>',
              '<tr><td><b>v4.19.1</b></td><td>修复：移动端结果页「继续」吸底（选完直接点，不用下滑）</td><td><code>09b1e55</code></td><td>+549</td></tr>\n<tr><td><b>v4.19.0</b></td>', 1)
entry = '''<h2 id="v4191">📱 v4.19.1 · 修复：移动端结果页「继续」吸底 <span class="sha">09b1e55</span></h2>
<div class="card">
<p>游玩反馈第三条：「手机上选完后还要下滑点继续」。结果页的「继续 ▶」按钮落在 <code>#stage</code> 内容流末尾——选项结算信息一多，就得下滑才够得着。</p>
<h3>修复（桌面不变，仅移动端）</h3>
<ul>
<li>结果页原按钮加 <code>.contBtn</code> 类；<code>renderResult</code> 末尾把「继续 ▶」<b>注入吸底行动栏</b>（<code>.contAct</code>）；</li>
<li>移动端：隐藏原按钮，行动栏显示橙色主行动「继续 ▶」——选完直接点，无需下滑；</li>
<li>桌面：<code>.contAct</code> 默认隐藏，一切照旧。</li>
</ul>
<h3>实现要点（首版踩坑已修）</h3>
<p><code>choose()</code> 结算后<b>直接调用 <code>renderResult</code>、不重渲整页</b>——因此行动栏按钮必须用 DOM 注入而非在 <code>renderGame</code> 里做条件渲染（首版走的后者，测试立刻抓到按钮不出现）。</p>
<h3>版本号规则变更（2026-10-05 起）</h3>
<p>小更新 / 修复<b>只加 0.0.1</b>（本版即首个补丁号版本）；新功能、新玩法、机制级改动才用次版本号。</p>
<h3>验证记录</h3>
<ul>
<li>验证套件 <b>20/20 项 · 505/505 断言</b>全部通过（<code>ui</code> 追加 6 断言，含 <code>choose(0)</code> → 结果模式 → 吸底继续 的端到端验证）；</li>
<li>重建（现 23 步）与仓库成品<b>逐字节一致</b>。</li>
</ul>
</div>
<h2 id="v4190">'''
s = s.replace('<h2 id="v4190">', entry, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('html done')

# ── 测试常量 ──
p = 'tools/test_changelog_page.js'
s = io.open(p, encoding='utf-8').read()
s = s.replace('secs.length === 33', 'secs.length === 34')
s = s.replace("kOf('v4.19.0') === 'eng', kOf('v4.19.0'));",
              "kOf('v4.19.0') === 'eng', kOf('v4.19.0'));\n  check('v4.19.1（继续吸底修复）→ 修复', kOf('v4.19.1') === 'fix', kOf('v4.19.1'));", 1)
s = s.replace("/v4\\.19\\.0/.test(h.querySelector('.vpill').textContent)",
              "/v4\\.19\\.1/.test(h.querySelector('.vpill').textContent)")
s = s.replace("vt.indexOf('v4.19.0') < 0", "vt.indexOf('v4.19.1') < 0")
s = s.replace('chips.length === 34', 'chips.length === 35')
s = s.replace('verChips.length === 33', 'verChips.length === 34')
s = s.replace('collapsed.length === 33 - 5', 'collapsed.length === 34 - 5')
s = s.replace("'v4.19.0', 'v4.18.0'", "'v4.19.1', 'v4.19.0', 'v4.18.0'")
s = s.replace('卡片数量未变（35 个）', '卡片数量未变（36 个）')
s = s.replace(".card').length === 35", ".card').length === 36")
s = s.replace('目录芯片被搬进工具条（33 版 + 附录）', '目录芯片被搬进工具条（34 版 + 附录）')
io.open(p, 'w', encoding='utf-8').write(s)
print('constants done')
