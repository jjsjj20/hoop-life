# -*- coding: utf-8 -*-
"""写 v4.20.3 更新日志（md+html）+ 测试常量。"""
import io

SHA = '9dfd1cc'

p = '更新日志.md'
s = io.open(p, encoding='utf-8').read()
s = s.replace('> 当前版本：**v4.20.2** · 最后更新：2026-10-05',
              '> 当前版本：**v4.20.3** · 最后更新：2026-10-05')
s = s.replace('| **v4.20.2**',
              '| **v4.20.3** | 修复：AI 只输出正文（统一输出格式规则 + 清洗兜底） | `__SHA__` | +901 |\n| **v4.20.2**'.replace('__SHA__', SHA), 1)
entry = '''
---

## 🤖 v4.20.3 · 修复：AI 只输出正文

**提交**：`__SHA__` · **文件**：583,252 字符（+901，相对 v4.20.2 的 582,351）

反馈：模型会把「草稿：…」「检查：…」「（约 160 字）」这类**自我说明与字数括注**
一起交出来——需要它只给正文。

### 修复（一处加规则 + 一处兜底，不动任何单条提示词）
1. **统一输出格式规则**：`AI.ask` 在系统提示词末尾追加——
   - 文本类：`【输出格式】只输出正文本身：直接给成文内容；不要前言、草稿、自检、
     字数统计、括注、说明或 Markdown 标记；不要复述要求，不要用引号把全文包起来。`
   - JSON 类：`【输出格式】只输出一个 JSON 对象本身：不要前言、说明、代码块或任何多余文字。`
   —— 一处生效，覆盖战报 / 颁奖 / 里程碑 / 终章 / 报纸 / AI 事件全部生成路径；
2. **清洗兜底**（`AI.san`）：去代码围栏、去「（约 N 字）」括注、去开头的寒暄/说明行
   （好的｜以下是｜草稿｜检查｜注｜字数…）、去整体包裹的引号、去行首标签——
   含句号的正文首句不会被误吃（有专门断言）。即使模型不守规矩，展示出来的也只是正文。

### 验证记录
- 验证套件 **22/22 项 · 562/562 断言**全绿（`ai` 追加 10 断言：规则注入 4 项 +
  清洗兜底 6 项，全部打桩验证）；
- 重建（现 29 步）与仓库成品**逐字节一致**。

---

## 🤖 v4.20.2 · 修复：AI 战报/报纸「接口响应缺少内容」'''.replace('__SHA__', SHA)
s = s.replace('\n---\n\n## 🤖 v4.20.2 · 修复：AI 战报/报纸「接口响应缺少内容」', entry, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('md done')

p = '更新日志.html'
s = io.open(p, encoding='utf-8').read()
s = s.replace('<span class="badge">当前版本 <b>v4.20.2</b></span><span class="badge">文件 <b>582,351</b> 字符</span><span class="badge">更新 <b>38</b> 个版本</span>',
              '<span class="badge">当前版本 <b>v4.20.3</b></span><span class="badge">文件 <b>583,252</b> 字符</span><span class="badge">更新 <b>39</b> 个版本</span>')
s = s.replace('<nav class="toc"><a href="#v4202">v4.20.2</a>',
              '<nav class="toc"><a href="#v4203">v4.20.3</a><a href="#v4202">v4.20.2</a>')
s = s.replace('<tr><td><b>v4.20.2</b></td>',
              '<tr><td><b>v4.20.3</b></td><td>修复：AI 只输出正文（统一输出格式规则 + 清洗兜底）</td><td><code>__SHA__</code></td><td>+901</td></tr>\n<tr><td><b>v4.20.2</b></td>'.replace('__SHA__', SHA), 1)
entry = '''<h2 id="v4203">🤖 v4.20.3 · 修复：AI 只输出正文 <span class="sha">__SHA__</span></h2>
<div class="card">
<p>反馈：模型会把「草稿：…」「检查：…」「（约 160 字）」这类<b>自我说明与字数括注</b>一起交出来——需要它只给正文。</p>
<h3>修复（一处加规则 + 一处兜底，不动任何单条提示词）</h3>
<ol>
<li><b>统一输出格式规则</b>：<code>AI.ask</code> 在系统提示词末尾追加——文本类「<code>只输出正文本身：直接给成文内容；不要前言、草稿、自检、字数统计、括注、说明或 Markdown 标记；不要复述要求，不要用引号把全文包起来。</code>」；JSON 类「<code>只输出一个 JSON 对象本身：不要前言、说明、代码块或任何多余文字。</code>」——一处生效，覆盖战报 / 颁奖 / 里程碑 / 终章 / 报纸 / AI 事件全部路径；</li>
<li><b>清洗兜底</b>（<code>AI.san</code>）：去代码围栏、去「（约 N 字）」括注、去开头寒暄/说明行（好的｜以下是｜草稿｜检查｜注｜字数…）、去整体包裹的引号、去行首标签——含句号的正文首句不会被误吃（有专门断言）。</li>
</ol>
<h3>验证记录</h3>
<ul>
<li>验证套件 <b>22/22 项 · 562/562 断言</b>全绿（<code>ai</code> 追加 10 断言：规则注入 4 项 + 清洗兜底 6 项，全部打桩验证）；</li>
<li>重建（现 29 步）与仓库成品<b>逐字节一致</b>。</li>
</ul>
</div>
<h2 id="v4202">'''.replace('__SHA__', SHA)
s = s.replace('<h2 id="v4202">', entry, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('html done')

p = 'tools/test_changelog_page.js'
s = io.open(p, encoding='utf-8').read()
s = s.replace('secs.length === 38', 'secs.length === 39')
s = s.replace("kOf('v4.20.2') === 'fix', kOf('v4.20.2'));",
              "kOf('v4.20.2') === 'fix', kOf('v4.20.2'));\n  check('v4.20.3（AI 只输出正文）→ 修复', kOf('v4.20.3') === 'fix', kOf('v4.20.3'));", 1)
s = s.replace("/v4\\.20\\.2/.test(h.querySelector('.vpill').textContent)",
              "/v4\\.20\\.3/.test(h.querySelector('.vpill').textContent)")
s = s.replace("vt.indexOf('v4.20.2') < 0", "vt.indexOf('v4.20.3') < 0")
s = s.replace('chips.length === 39', 'chips.length === 40')
s = s.replace('verChips.length === 38', 'verChips.length === 39')
s = s.replace('collapsed.length === 38 - 5', 'collapsed.length === 39 - 5')
s = s.replace("'v4.20.2', 'v4.20.1'", "'v4.20.3', 'v4.20.2', 'v4.20.1'")
s = s.replace('卡片数量未变（40 个）', '卡片数量未变（41 个）')
s = s.replace(".card').length === 40", ".card').length === 41")
s = s.replace('目录芯片被搬进工具条（38 版 + 附录）', '目录芯片被搬进工具条（39 版 + 附录）')
io.open(p, 'w', encoding='utf-8').write(s)
print('constants done')
