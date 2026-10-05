# -*- coding: utf-8 -*-
"""写 v4.20.5 更新日志（md+html）+ 测试常量。"""
import io

SHA = 'f3b5358'

p = '更新日志.md'
s = io.open(p, encoding='utf-8').read()
s = s.replace('> 当前版本：**v4.20.4** · 最后更新：2026-10-05',
              '> 当前版本：**v4.20.5** · 最后更新：2026-10-05')
s = s.replace('| **v4.20.4**',
              '| **v4.20.5** | 修复：回声判定收紧（正常报纸不再被误判）+ 报纸重试一次 | `__SHA__` | +739 |\n| **v4.20.4**'.replace('__SHA__', SHA), 1)
entry = '''
---

## 🤖 v4.20.5 · 修复：体育报被误判「复述要求」

**提交**：`__SHA__` · **文件**：584,940 字符（+739，相对 v4.20.4 的 584,201）

反馈：「体育报说模型在复述要求」——v4.20.4 的回声检测**误报**了。
根因：判定过宽——事实标签（球员：/结果：…）命中 **2 个**即判回声，
而报纸正文天然会引用这些标签（"结果：勇士取胜"这类写法很常见）。

### 修复
1. **判定改打分制**（`AI.looksLikeEcho`）：
   - 强特征命中 **1 个**即判回声（只在提示词里出现的词）：`不能编造` / `只使用给定` /
     `【任务】` / `【事实】` / `不要复述`；
   - 弱特征需 **≥2 个**：`要求：` / `字数` / `Markdown`；
   - 事实标签需 **≥3 个**（真回声通常带 5~6 个，正常文章引 1~2 个不再误伤）；
2. **报纸与战报同待遇**：判为回声 → **带加强指令重试一次** → 仍回声才报错且不写缓存
   （此前报纸是直接报错，没有第二次机会）。

### 验证记录
- 验证套件 **22/22 项 · 583/583 断言**全绿（`ai` 追加 9 断言：
  **误报回归 5 项**——真实报纸正文（含【头版】【流言板】"据悉"等）不判回声、
  只引 2 个标签不判、"要求"单次出现不判、强特征仍能识别、3 个标签判回声；
  报纸重试与缓存 4 项）；
- 重建（现 31 步）与仓库成品**逐字节一致**。

---

## 🤖 v4.20.4 · 修复：AI 把要求复述回来了（回声检测 + 重试）'''.replace('__SHA__', SHA)
s = s.replace('\n---\n\n## 🤖 v4.20.4 · 修复：AI 把要求复述回来了（回声检测 + 重试）', entry, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('md done')

p = '更新日志.html'
s = io.open(p, encoding='utf-8').read()
s = s.replace('<span class="badge">当前版本 <b>v4.20.4</b></span><span class="badge">文件 <b>584,201</b> 字符</span><span class="badge">更新 <b>40</b> 个版本</span>',
              '<span class="badge">当前版本 <b>v4.20.5</b></span><span class="badge">文件 <b>584,940</b> 字符</span><span class="badge">更新 <b>41</b> 个版本</span>')
s = s.replace('<nav class="toc"><a href="#v4204">v4.20.4</a>',
              '<nav class="toc"><a href="#v4205">v4.20.5</a><a href="#v4204">v4.20.4</a>')
s = s.replace('<tr><td><b>v4.20.4</b></td>',
              '<tr><td><b>v4.20.5</b></td><td>修复：回声判定收紧（正常报纸不再被误判）+ 报纸重试一次</td><td><code>__SHA__</code></td><td>+739</td></tr>\n<tr><td><b>v4.20.4</b></td>'.replace('__SHA__', SHA), 1)
entry = '''<h2 id="v4205">🤖 v4.20.5 · 修复：体育报被误判「复述要求」 <span class="sha">__SHA__</span></h2>
<div class="card">
<p>反馈：「体育报说模型在复述要求」——v4.20.4 的回声检测<b>误报</b>了。根因：判定过宽——事实标签（球员：/结果：…）命中 <b>2 个</b>即判回声，而报纸正文天然会引用这些标签。</p>
<h3>修复</h3>
<ol>
<li><b>判定改打分制</b>（<code>AI.looksLikeEcho</code>）：强特征命中 <b>1 个</b>即判回声（只在提示词里出现的词：不能编造 / 只使用给定 / 【任务】 / 【事实】 / 不要复述）；弱特征（要求：/字数/Markdown）需 ≥2；事实标签需 <b>≥3</b>（真回声通常带 5~6 个，正常文章引 1~2 个不再误伤）；</li>
<li><b>报纸与战报同待遇</b>：判为回声 → 带加强指令重试一次 → 仍回声才报错且不写缓存（此前报纸直接报错，没有第二次机会）。</li>
</ol>
<h3>验证记录</h3>
<ul>
<li>验证套件 <b>22/22 项 · 583/583 断言</b>全绿（<code>ai</code> 追加 9 断言：<b>误报回归 5 项</b>——真实报纸正文（含【头版】【流言板】"据悉"等）不判回声、只引 2 个标签不判、"要求"单次出现不判、强特征仍能识别、3 个标签判回声；报纸重试与缓存 4 项）；</li>
<li>重建（现 31 步）与仓库成品<b>逐字节一致</b>。</li>
</ul>
</div>
<h2 id="v4204">'''.replace('__SHA__', SHA)
s = s.replace('<h2 id="v4204">', entry, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('html done')

p = 'tools/test_changelog_page.js'
s = io.open(p, encoding='utf-8').read()
s = s.replace('secs.length === 40', 'secs.length === 41')
s = s.replace("kOf('v4.20.4') === 'fix', kOf('v4.20.4'));",
              "kOf('v4.20.4') === 'fix', kOf('v4.20.4'));\n  check('v4.20.5（回声判定收紧）→ 修复', kOf('v4.20.5') === 'fix', kOf('v4.20.5'));", 1)
s = s.replace("/v4\\.20\\.4/.test(h.querySelector('.vpill').textContent)",
              "/v4\\.20\\.5/.test(h.querySelector('.vpill').textContent)")
s = s.replace("vt.indexOf('v4.20.4') < 0", "vt.indexOf('v4.20.5') < 0")
s = s.replace('chips.length === 41', 'chips.length === 42')
s = s.replace('verChips.length === 40', 'verChips.length === 41')
s = s.replace('collapsed.length === 40 - 5', 'collapsed.length === 41 - 5')
s = s.replace("'v4.20.4', 'v4.20.3'", "'v4.20.5', 'v4.20.4', 'v4.20.3'")
s = s.replace('卡片数量未变（42 个）', '卡片数量未变（43 个）')
s = s.replace(".card').length === 42", ".card').length === 43")
s = s.replace('目录芯片被搬进工具条（40 版 + 附录）', '目录芯片被搬进工具条（41 版 + 附录）')
io.open(p, 'w', encoding='utf-8').write(s)
print('constants done')
