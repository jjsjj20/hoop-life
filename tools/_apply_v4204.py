# -*- coding: utf-8 -*-
"""写 v4.20.4 更新日志（md+html）+ 测试常量。"""
import io

SHA = '0ce8c31'

p = '更新日志.md'
s = io.open(p, encoding='utf-8').read()
s = s.replace('> 当前版本：**v4.20.3** · 最后更新：2026-10-05',
              '> 当前版本：**v4.20.4** · 最后更新：2026-10-05')
s = s.replace('| **v4.20.3**',
              '| **v4.20.4** | 修复：AI 回声检测——复读要求/事实不入缓存，自动重试一次 | `__SHA__` | +949 |\n| **v4.20.3**'.replace('__SHA__', SHA), 1)
entry = '''
---

## 🤖 v4.20.4 · 修复：AI 把要求复述回来了（回声检测 + 重试）

**提交**：`__SHA__` · **文件**：584,201 字符（+949，相对 v4.20.3 的 583,252）

反馈：「还是这样」——模型把**任务要求与事实原样复述**回来（甚至重复两遍后截断），
而且这类输出一旦写入缓存，同一个事件会一直复现同样的垃圾。

### 修复
1. **回声识别** `AI.looksLikeEcho()`：命中指令词（要求：/不能编造/只使用给定/
   Markdown/字数/【任务】/【事实】）或命中 ≥2 个事实标签（球员：/比赛：/结果：/
   个人数据：/系统旁白：/分节得分：）即判为回声；
2. **自动重试**：战报/颁奖/里程碑/终章类生成若判为回声 → **带加强指令重试一次**
   （"【再次强调】只写正文，不要复述上面的要求或事实。"）；仍为回声 → 明确报错
   「模型在复述要求，请重试或换一个模型」；
3. **不写缓存**：回声输出**绝不入缓存**（报纸路径同理）——避免垃圾长期复现；
4. **规则与提示词**：`RULE_ONLY` 追加「不要复述题目、事实或要求」；
   战报用户提示词改为【任务】/【事实】分栏，任务行明确"只写正文"。

### 验证记录
- 验证套件 **22/22 项 · 572/572 断言**全绿（`ai` 追加 8 断言：回声识别 3 项 +
  重试链路与缓存策略 5 项，全部打桩验证——含"首次回声→重试成功→缓存干净正文"、
  "连续回声→明确报错且不写缓存"两条端到端）；
- 重建（现 30 步）与仓库成品**逐字节一致**。

---

## 🤖 v4.20.3 · 修复：AI 只输出正文'''.replace('__SHA__', SHA)
s = s.replace('\n---\n\n## 🤖 v4.20.3 · 修复：AI 只输出正文', entry, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('md done')

p = '更新日志.html'
s = io.open(p, encoding='utf-8').read()
s = s.replace('<span class="badge">当前版本 <b>v4.20.3</b></span><span class="badge">文件 <b>583,252</b> 字符</span><span class="badge">更新 <b>39</b> 个版本</span>',
              '<span class="badge">当前版本 <b>v4.20.4</b></span><span class="badge">文件 <b>584,201</b> 字符</span><span class="badge">更新 <b>40</b> 个版本</span>')
s = s.replace('<nav class="toc"><a href="#v4203">v4.20.3</a>',
              '<nav class="toc"><a href="#v4204">v4.20.4</a><a href="#v4203">v4.20.3</a>')
s = s.replace('<tr><td><b>v4.20.3</b></td>',
              '<tr><td><b>v4.20.4</b></td><td>修复：AI 回声检测——复读要求/事实不入缓存，自动重试一次</td><td><code>__SHA__</code></td><td>+949</td></tr>\n<tr><td><b>v4.20.3</b></td>'.replace('__SHA__', SHA), 1)
entry = '''<h2 id="v4204">🤖 v4.20.4 · 修复：AI 把要求复述回来了（回声检测 + 重试） <span class="sha">__SHA__</span></h2>
<div class="card">
<p>反馈：「还是这样」——模型把<b>任务要求与事实原样复述</b>回来（甚至重复两遍后截断），而且这类输出一旦写入缓存，同一个事件会一直复现同样的垃圾。</p>
<h3>修复</h3>
<ol>
<li><b>回声识别</b> <code>AI.looksLikeEcho()</code>：命中指令词（要求：/不能编造/只使用给定/Markdown/字数/【任务】/【事实】）或命中 ≥2 个事实标签（球员：/比赛：/结果：/个人数据：/系统旁白：/分节得分：）即判为回声；</li>
<li><b>自动重试</b>：判为回声 → <b>带加强指令重试一次</b>（"【再次强调】只写正文，不要复述上面的要求或事实。"）；仍为回声 → 明确报错「模型在复述要求，请重试或换一个模型」；</li>
<li><b>不写缓存</b>：回声输出<b>绝不入缓存</b>（报纸路径同理）——避免垃圾长期复现；</li>
<li><b>规则与提示词</b>：<code>RULE_ONLY</code> 追加「不要复述题目、事实或要求」；战报用户提示词改为【任务】/【事实】分栏。</li>
</ol>
<h3>验证记录</h3>
<ul>
<li>验证套件 <b>22/22 项 · 572/572 断言</b>全绿（<code>ai</code> 追加 8 断言，含"首次回声→重试成功→缓存干净正文"、"连续回声→明确报错且不写缓存"两条端到端，全部打桩验证）；</li>
<li>重建（现 30 步）与仓库成品<b>逐字节一致</b>。</li>
</ul>
</div>
<h2 id="v4203">'''.replace('__SHA__', SHA)
s = s.replace('<h2 id="v4203">', entry, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('html done')

p = 'tools/test_changelog_page.js'
s = io.open(p, encoding='utf-8').read()
s = s.replace('secs.length === 39', 'secs.length === 40')
s = s.replace("kOf('v4.20.3') === 'fix', kOf('v4.20.3'));",
              "kOf('v4.20.3') === 'fix', kOf('v4.20.3'));\n  check('v4.20.4（AI 回声检测）→ 修复', kOf('v4.20.4') === 'fix', kOf('v4.20.4'));", 1)
s = s.replace("/v4\\.20\\.3/.test(h.querySelector('.vpill').textContent)",
              "/v4\\.20\\.4/.test(h.querySelector('.vpill').textContent)")
s = s.replace("vt.indexOf('v4.20.3') < 0", "vt.indexOf('v4.20.4') < 0")
s = s.replace('chips.length === 40', 'chips.length === 41')
s = s.replace('verChips.length === 39', 'verChips.length === 40')
s = s.replace('collapsed.length === 39 - 5', 'collapsed.length === 40 - 5')
s = s.replace("'v4.20.3', 'v4.20.2'", "'v4.20.4', 'v4.20.3', 'v4.20.2'")
s = s.replace('卡片数量未变（41 个）', '卡片数量未变（42 个）')
s = s.replace(".card').length === 41", ".card').length === 42")
s = s.replace('目录芯片被搬进工具条（39 版 + 附录）', '目录芯片被搬进工具条（40 版 + 附录）')
io.open(p, 'w', encoding='utf-8').write(s)
print('constants done')
