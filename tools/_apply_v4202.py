# -*- coding: utf-8 -*-
"""写 v4.20.2 更新日志（md+html）+ 测试常量。"""
import io

SHA = '36f2d7c'

# ── md ──
p = '更新日志.md'
s = io.open(p, encoding='utf-8').read()
s = s.replace('> 当前版本：**v4.20.1** · 最后更新：2026-10-05',
              '> 当前版本：**v4.20.2** · 最后更新：2026-10-05')
s = s.replace('| **v4.20.1**',
              '| **v4.20.2** | 修复：AI 战报/报纸「接口响应缺少内容」（兼容思考型模型 + 自动重试） | `__SHA__` | +1,293 |\n| **v4.20.1**'.replace('__SHA__', SHA), 1)
entry = '''
---

## 🤖 v4.20.2 · 修复：AI 战报/报纸「接口响应缺少内容」

**提交**：`__SHA__` · **文件**：582,351 字符（+1,293，相对 v4.20.1 的 581,058）

反馈：「AI 战报和其他生成不了，报『接口响应缺少内容』，但 AI 事件可以生成。」

### 根因
三类生成共用同一个 `AI.ask`，**差异只在参数**：
- AI 事件：`mt 800` + JSON 模式（**成功**）
- 战报 / 里程碑 / 赛季 / 报纸：**默认 `mt 360`**（失败）

思考型模型（reasoning 类，如 R1/o 系列与第三方推理模型）会把 360 的预算吃在
**思考轨迹**上，留给正式内容的 token 所剩无几 → `choices[0].message.content` 为空
→ 被误判成「接口不支持」。此外还有两处加重症状：15 秒超时对大预算生成偏紧；
响应解析只认 `content` 字符串一种形状。

### 修复
1. **响应形状兼容** `AI.textOf()`：content 字符串 / 数组分片 / `reasoning_content` /
   `choices[0].text` / `output_text` 五种形状都能取到正文；
2. **预算与超时**：默认 `mt 360→900`；超时 `15s→20s`（大预算 30s）；
3. **空内容自动重试**：抬预算到 ≥1200 并去掉 JSON 模式重试一次——
   把「思考吃光预算」这条最常见的死路直接走通（用户无感知）；
4. **诊断信息**：失败提示带 `finish_reason`，下次出问题一眼定位；
5. **长文不再被截断**：`AI.san` 支持自定义上限，报纸等长文放宽到 1200 字。

### 验证记录
- 验证套件 **22/22 项 · 550/550 断言**全绿（新增 `ai` 14 断言：
  五种响应形状解析 / 默认预算 900 / 空内容→抬预算重试链路 / 错误带 finish_reason /
  san 自定义上限），全部用打桩 fetch 验证，无需真实网络；
- 重建（现 28 步）与仓库成品**逐字节一致**。

---

## ⚖️ v4.20.1 · 数值对齐：荣誉不再「每季一大把」'''.replace('__SHA__', SHA)
s = s.replace('\n---\n\n## ⚖️ v4.20.1 · 数值对齐：荣誉不再「每季一大把」', entry, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('md done')

# ── html ──
p = '更新日志.html'
s = io.open(p, encoding='utf-8').read()
s = s.replace('<span class="badge">当前版本 <b>v4.20.1</b></span><span class="badge">文件 <b>581,058</b> 字符</span><span class="badge">更新 <b>37</b> 个版本</span>',
              '<span class="badge">当前版本 <b>v4.20.2</b></span><span class="badge">文件 <b>582,351</b> 字符</span><span class="badge">更新 <b>38</b> 个版本</span>')
s = s.replace('<nav class="toc"><a href="#v4201">v4.20.1</a>',
              '<nav class="toc"><a href="#v4202">v4.20.2</a><a href="#v4201">v4.20.1</a>')
s = s.replace('<tr><td><b>v4.20.1</b></td>',
              '<tr><td><b>v4.20.2</b></td><td>修复：AI 战报/报纸「接口响应缺少内容」（兼容思考型模型 + 自动重试）</td><td><code>__SHA__</code></td><td>+1,293</td></tr>\n<tr><td><b>v4.20.1</b></td>'.replace('__SHA__', SHA), 1)
entry = '''<h2 id="v4202">🤖 v4.20.2 · 修复：AI 战报/报纸「接口响应缺少内容」 <span class="sha">__SHA__</span></h2>
<div class="card">
<p>反馈：「AI 战报和其他生成不了，报『接口响应缺少内容』，但 AI 事件可以生成。」</p>
<h3>根因</h3>
<p>三类生成共用同一个 <code>AI.ask</code>，<b>差异只在参数</b>：AI 事件用 <code>mt 800</code> + JSON 模式（成功）；战报/里程碑/赛季/报纸用<b>默认 <code>mt 360</code></b>（失败）。思考型模型（reasoning 类）会把 360 的预算吃在<b>思考轨迹</b>上，留给正式内容的 token 所剩无几 → <code>choices[0].message.content</code> 为空 → 被误判成「接口不支持」。另有两点加重症状：15 秒超时偏紧；响应解析只认一种形状。</p>
<h3>修复</h3>
<ol>
<li><b>响应形状兼容</b> <code>AI.textOf()</code>：content 字符串 / 数组分片 / <code>reasoning_content</code> / <code>choices[0].text</code> / <code>output_text</code> 五种形状都能取到正文；</li>
<li><b>预算与超时</b>：默认 <code>mt 360→900</code>；超时 <code>15s→20s</code>（大预算 30s）；</li>
<li><b>空内容自动重试</b>：抬预算到 ≥1200 并去掉 JSON 模式重试一次——用户无感知地走通「思考吃光预算」这条死路；</li>
<li><b>诊断信息</b>：失败提示带 <code>finish_reason</code>；</li>
<li><b>长文不再被截断</b>：<code>AI.san</code> 支持自定义上限，报纸放宽到 1200 字。</li>
</ol>
<h3>验证记录</h3>
<ul>
<li>验证套件 <b>22/22 项 · 550/550 断言</b>全绿（新增 <code>ai</code> 14 断言，全部用打桩 fetch 验证，无需真实网络）；</li>
<li>重建（现 28 步）与仓库成品<b>逐字节一致</b>。</li>
</ul>
</div>
<h2 id="v4201">'''.replace('__SHA__', SHA)
s = s.replace('<h2 id="v4201">', entry, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('html done')

# ── 测试常量 ──
p = 'tools/test_changelog_page.js'
s = io.open(p, encoding='utf-8').read()
s = s.replace('secs.length === 37', 'secs.length === 38')
s = s.replace("kOf('v4.20.1') === 'play', kOf('v4.20.1'));",
              "kOf('v4.20.1') === 'play', kOf('v4.20.1'));\n  check('v4.20.2（AI 修复）→ 修复', kOf('v4.20.2') === 'fix', kOf('v4.20.2'));", 1)
s = s.replace("/v4\\.20\\.1/.test(h.querySelector('.vpill').textContent)",
              "/v4\\.20\\.2/.test(h.querySelector('.vpill').textContent)")
s = s.replace("vt.indexOf('v4.20.1') < 0", "vt.indexOf('v4.20.2') < 0")
s = s.replace('chips.length === 38', 'chips.length === 39')
s = s.replace('verChips.length === 37', 'verChips.length === 38')
s = s.replace('collapsed.length === 37 - 5', 'collapsed.length === 38 - 5')
s = s.replace("'v4.20.1', 'v4.20.0'", "'v4.20.2', 'v4.20.1', 'v4.20.0'")
s = s.replace('卡片数量未变（39 个）', '卡片数量未变（40 个）')
s = s.replace(".card').length === 39", ".card').length === 40")
s = s.replace('目录芯片被搬进工具条（37 版 + 附录）', '目录芯片被搬进工具条（38 版 + 附录）')
io.open(p, 'w', encoding='utf-8').write(s)
print('constants done')
