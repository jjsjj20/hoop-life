# -*- coding: utf-8 -*-
"""写 v4.21.0 更新日志（md+html）+ 测试常量。"""
import io

SHA = 'b964210'

p = '更新日志.md'
s = io.open(p, encoding='utf-8').read()
s = s.replace('> 当前版本：**v4.20.5** · 最后更新：2026-10-05',
              '> 当前版本：**v4.21.0** · 最后更新：2026-10-05')
s = s.replace('| **v4.20.5**',
              '| **v4.21.0** | 移除：AI 点评层整体删除（−31,290 字符，回归零外部依赖） | `__SHA__` | −31,290 |\n| **v4.20.5**'.replace('__SHA__', SHA), 1)
entry = '''
---

## 🧹 v4.21.0 · 移除：AI 点评层整体删除

**提交**：`__SHA__` · **文件**：549,943 字符（**−31,290**，相对 v4.20.5 的 584,940）

### 评估过程
对 AI 子系统做了完整盘点（规模 / 集成面 / 测试覆盖 / 依赖）：

| 维度 | 实测 |
| :-- | :-- |
| 规模 | 约 650 行，占全文件 6%（10,860 行） |
| 构成 | 传输层（ask/textOf/清洗/缓存）· 5 个文案生成（战报/颁奖/里程碑/终章/报纸）· AI 事件注入（47 处引用）· 设置面板 |
| 集成面 | **仅 2 个按钮** + 模块自包装的 getEvent 钩子——模块内符号在模块外**零引用** |
| 测试 | `test_ai.js` 41 断言（全部打桩，无网络） |
| 依赖 | **全项目唯一的网络依赖 + 唯一的凭据依赖**（BYOK） |

### 为什么删除而不是重构
1. **残余失败的根因不在本仓库**：四轮补丁（v4.20.2~v4.20.5）已修尽代码侧的全部已知问题
   ——空内容（推理模型吃光预算）、复述要求（回声）、判定误报、字数括注、超时、JSON 不合规。
   剩下的失败（模型复读、内容为空、格式不听话）**取决于玩家自配的模型与网络**，
   代码再改也无法把可靠性上限抬上去。
2. **代价与收益已经倒挂**：为支撑一个默认关闭的实验功能，付出 6% 代码量、一套设置面板、
   41 条测试，以及"用户可见的失败"风险——而**失败无法由我方修复**。
3. **依赖洁癖**：这是离线优先、零外部依赖的单文件游戏里唯一的网络/凭据依赖；
   删除后整个产品的行为**完全确定、可离线复现**。
4. **删除面干净且可逆**：模块自包含（模块外零引用符号）、外部只有 2 个按钮，
   实现留在 git 历史里（含本模块的最后一个提交 `b964210^`），随时可恢复。

### 移除清单
- 模块本体（IIFE 约 650 行）· `AI_CSS` 样式 · 设置/密钥面板 · 本地缓存与键 · AI 事件注入（getEvent 包装与渲染槽位）
- 行动栏「🤖 AI」按钮 · ☰ 更多菜单「📰 新闻」入口
- 测试：删除 `test_ai.js`（41 断言）与生成器；`test_robustness` 移除 AI 密钥块（18 行）；
  `test_pwa_card` 移除 AI 离线断言；`test_p7` 行动栏断言更新
- 构建管线：4 个 AI 补丁步骤（㉖~㉙）合并为单一步骤 ㉚ `patch_remove_ai.py`
- **连带修复**：v4.15 的 SW 注册块当初插在 AI 模块内部（`AI.mount` 之前）被一并删除——
  已放回模块外的稳定位置，PWA 注册守卫断言恢复通过

### 验证记录
- 验证套件 **21/21 项 · 535/535 断言**全绿（AI 的 41 断言随功能移除，其余全部保留）；
- **端到端实跑**：2 个生涯 × 各 25 季完整走完（事件流 / 结算 / 选秀 / 退役）无异常；
- 重建（现 31 步）与仓库成品**逐字节一致**。

### 如果将来想恢复
```bash
git checkout b964210^ -- 篮球人生.html       # 取回含 AI 层的上一版单文件
# 或：从 git 历史恢复 tools/build/patch_ai_*.py 与 test_ai.js（均在 b964210^ 及更早提交里）
```
建议若恢复，只恢复「面板文案类」（战报/颁奖/里程碑/终章/报纸），**不要**恢复 AI 事件注入
——前者只是叠加层，后者动的是核心事件流。

---

## 🤖 v4.20.5 · 修复：体育报被误判「复述要求」'''.replace('__SHA__', SHA)
s = s.replace('\n---\n\n## 🤖 v4.20.5 · 修复：体育报被误判「复述要求」', entry, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('md done')

p = '更新日志.html'
s = io.open(p, encoding='utf-8').read()
s = s.replace('<span class="badge">当前版本 <b>v4.20.5</b></span><span class="badge">文件 <b>584,940</b> 字符</span><span class="badge">更新 <b>41</b> 个版本</span>',
              '<span class="badge">当前版本 <b>v4.21.0</b></span><span class="badge">文件 <b>549,943</b> 字符</span><span class="badge">更新 <b>42</b> 个版本</span>')
s = s.replace('<nav class="toc"><a href="#v4205">v4.20.5</a>',
              '<nav class="toc"><a href="#v4210">v4.21.0</a><a href="#v4205">v4.20.5</a>')
s = s.replace('<tr><td><b>v4.20.5</b></td>',
              '<tr><td><b>v4.21.0</b></td><td>移除：AI 点评层整体删除（−31,290 字符，回归零外部依赖）</td><td><code>__SHA__</code></td><td>−31,290</td></tr>\n<tr><td><b>v4.20.5</b></td>'.replace('__SHA__', SHA), 1)
entry = '''<h2 id="v4210">🧹 v4.21.0 · 移除：AI 点评层整体删除 <span class="sha">__SHA__</span></h2>
<div class="card">
<p><b>文件</b>：549,943 字符（<b>−31,290</b>，相对 v4.20.5 的 584,940）——代码量减少 6%。</p>
<h3>评估过程</h3>
<div class="tw"><table>
<tr><th>维度</th><th>实测</th></tr>
<tr><td>规模</td><td>约 650 行，占全文件 6%（10,860 行）</td></tr>
<tr><td>构成</td><td>传输层 · 5 个文案生成（战报/颁奖/里程碑/终章/报纸）· AI 事件注入（47 处引用）· 设置面板</td></tr>
<tr><td>集成面</td><td><b>仅 2 个按钮</b> + 模块自包装的 getEvent 钩子——模块内符号在模块外<b>零引用</b></td></tr>
<tr><td>测试</td><td><code>test_ai.js</code> 41 断言（全部打桩，无网络）</td></tr>
<tr><td>依赖</td><td><b>全项目唯一的网络依赖 + 唯一的凭据依赖</b>（BYOK）</td></tr>
</table></div>
<h3>为什么删除而不是重构</h3>
<ol>
<li><b>残余失败的根因不在本仓库</b>：四轮补丁（v4.20.2~v4.20.5）已修尽代码侧的全部已知问题——空内容、复述要求、判定误报、字数括注、超时、JSON 不合规。剩下的失败取决于玩家自配的模型与网络，代码再改也无法把可靠性上限抬上去。</li>
<li><b>代价与收益倒挂</b>：为支撑一个默认关闭的实验功能，付出 6% 代码量、一套设置面板、41 条测试，以及"用户可见且我方无法修复"的失败风险。</li>
<li><b>依赖洁癖</b>：这是离线优先、零外部依赖的单文件游戏里唯一的网络/凭据依赖；删除后整个产品的行为完全确定、可离线复现。</li>
<li><b>删除面干净且可逆</b>：模块自包含、外部只有 2 个按钮，实现留在 git 历史里，随时可恢复。</li>
</ol>
<h3>移除清单</h3>
<ul>
<li>模块本体（IIFE 约 650 行）· <code>AI_CSS</code> · 设置/密钥面板 · 本地缓存与键 · AI 事件注入（getEvent 包装与渲染槽位）</li>
<li>行动栏「🤖 AI」按钮 · ☰ 更多菜单「📰 新闻」入口</li>
<li>测试：删除 <code>test_ai.js</code> 与生成器；<code>test_robustness</code> 移除 AI 密钥块；<code>test_pwa_card</code> 移除 AI 离线断言；<code>test_p7</code> 行动栏断言更新</li>
<li>构建管线：4 个 AI 补丁步骤合并为 ㉚ <code>patch_remove_ai.py</code></li>
<li><b>连带修复</b>：v4.15 的 SW 注册块当初插在 AI 模块内部被一并删除——已放回模块外的稳定位置，PWA 注册守卫断言恢复通过</li>
</ul>
<h3>验证记录</h3>
<ul>
<li>验证套件 <b>21/21 项 · 535/535 断言</b>全绿；</li>
<li><b>端到端实跑</b>：2 个生涯 × 各 25 季完整走完（事件流 / 结算 / 选秀 / 退役）无异常；</li>
<li>重建（现 31 步）与仓库成品<b>逐字节一致</b>。</li>
</ul>
<h3>如果将来想恢复</h3>
<p><code>git checkout b964210^ -- 篮球人生.html</code> 可取回含 AI 层的上一版单文件。建议若恢复，只恢复「面板文案类」（战报/颁奖/里程碑/终章/报纸），<b>不要</b>恢复 AI 事件注入——前者只是叠加层，后者动的是核心事件流。</p>
</div>
<h2 id="v4205">'''.replace('__SHA__', SHA)
s = s.replace('<h2 id="v4205">', entry, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('html done')

p = 'tools/test_changelog_page.js'
s = io.open(p, encoding='utf-8').read()
s = s.replace('secs.length === 41', 'secs.length === 42')
s = s.replace("kOf('v4.20.5') === 'fix', kOf('v4.20.5'));",
              "kOf('v4.20.5') === 'fix', kOf('v4.20.5'));\n  check('v4.21.0（移除 AI 层）→ 修复', kOf('v4.21.0') === 'fix', kOf('v4.21.0'));", 1)
s = s.replace("/v4\\.20\\.5/.test(h.querySelector('.vpill').textContent)",
              "/v4\\.21\\.0/.test(h.querySelector('.vpill').textContent)")
s = s.replace("vt.indexOf('v4.20.5') < 0", "vt.indexOf('v4.21.0') < 0")
s = s.replace('chips.length === 42', 'chips.length === 43')
s = s.replace('verChips.length === 41', 'verChips.length === 42')
s = s.replace('collapsed.length === 41 - 5', 'collapsed.length === 42 - 5')
s = s.replace("'v4.20.5', 'v4.20.4'", "'v4.21.0', 'v4.20.5', 'v4.20.4'")
s = s.replace('卡片数量未变（43 个）', '卡片数量未变（44 个）')
s = s.replace(".card').length === 43", ".card').length === 44")
s = s.replace("table').length === 19", "table').length === 20")
s = s.replace('表格数量未变（19 个）', '表格数量未变（20 个）')
s = s.replace('目录芯片被搬进工具条（41 版 + 附录）', '目录芯片被搬进工具条（42 版 + 附录）')
io.open(p, 'w', encoding='utf-8').write(s)
print('constants done')
