# -*- coding: utf-8 -*-
"""写 v4.17.0 更新日志（md+html）+ 测试常量 + 计划勾选 R2。"""
import io

# ── 更新日志.md ──
p = '更新日志.md'
s = io.open(p, encoding='utf-8').read()
s = s.replace('> 当前版本：**v4.16.0** · 最后更新：2026-10-04',
              '> 当前版本：**v4.17.0** · 最后更新：2026-10-04')
s = s.replace('| **v4.16.0**',
              '| **v4.17.0** | R2 青训补强：40 条青训事件（池 11→21）· 青训段节奏数据补齐（4 年重复率 0.0%） | `R2` | +13,100 |\n| **v4.16.0**', 1)
entry = '''
---

## 🏫 v4.17.0 · R2 青训体验补强（第二周期提案收官）

**提交**：R2 系列提交 · **文件**：576,886 字符（+13,100，相对 v4.16.0 的 563,786）

### 青训四季池各补 10 条事件（yp/ys/ya/yw 12~21，共 40 条）
原各 11 条在 4 年窗口（16 次抽取）下重复风险天然偏高。新增题材：生长痛、父亲工地、
分班考试、骨龄检测风波、宿舍篮球夜、淘汰边缘、教练调离、军训、中暑、发育焦虑、
外婆的夏天、兄弟转会死敌、末位淘汰、夜不归寝、教练的儿子、妈妈的来信、
冬训地狱、病房探访、跨年夜、压岁钱、技术定型危机、想放弃的夜晚、国青来信……
其中 12 条戏剧事件全部手工登记 `EV_KIND_OVERRIDE`。

### 验收数据（SIM_AGE=15 青训起步，30 生涯 / 120 青训赛季实测）

| 指标 | 结果 | 验收线 |
|:--|:--:|:--:|
| 青训段（15~18 岁）4 年窗口事件重复率 | **0.0%**（0/693） | <5% ✓ |
| 池事件数 | **21 条/池**（11+10） | ≥20 ✓ |
| 青训段戏剧占比 | **49.4%** | — |
| 15 岁起步模拟 | 30 生涯全部成功 | — |

### 工程面
- `sim_pacing.js` 支持 `SIM_AGE`（15 岁青训起步）/`SIM_ONE`（单生涯）参数；
- 新增 `test_r2.js`（15 断言：池规模/戏剧密度/题材广度/override/SIM_AGE 支持）；
- `tools/build_all.py` 重建（现 20 步）与仓库成品**逐字节一致**。

---

## ⚖️ v4.16.0 · R3 摆烂机制实装（签位与战绩联动）'''
s = s.replace('\n---\n\n## ⚖️ v4.16.0 · R3 摆烂机制实装（签位与战绩联动）', entry, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('md done')

# ── 更新日志.html ──
p = '更新日志.html'
s = io.open(p, encoding='utf-8').read()
s = s.replace('<span class="badge">当前版本 <b>v4.16.0</b></span><span class="badge">文件 <b>563,786</b> 字符</span><span class="badge">更新 <b>30</b> 个版本</span>',
              '<span class="badge">当前版本 <b>v4.17.0</b></span><span class="badge">文件 <b>576,886</b> 字符</span><span class="badge">更新 <b>31</b> 个版本</span>')
s = s.replace('<nav class="toc"><a href="#v4160">v4.16.0</a>',
              '<nav class="toc"><a href="#v4170">v4.17.0</a><a href="#v4160">v4.16.0</a>')
s = s.replace('<tr><td><b>v4.16.0</b></td>',
              '<tr><td><b>v4.17.0</b></td><td>R2 青训补强：40 条青训事件（池 11→21）· 青训段节奏数据补齐（4 年重复率 0.0%）</td><td>R2 系列</td><td>+13,100</td></tr>\n<tr><td><b>v4.16.0</b></td>', 1)
entry = '''<h2 id="v4170">🏫 v4.17.0 · R2 青训体验补强（第二周期提案收官） <span class="sha">R2 系列</span></h2>
<div class="card">
<h3>青训四季池各补 10 条事件（yp/ys/ya/yw 12~21，共 40 条）</h3>
<p>原各 11 条在 4 年窗口（16 次抽取）下重复风险天然偏高。新增题材：生长痛、父亲工地、分班考试、骨龄检测风波、宿舍篮球夜、淘汰边缘、教练调离、军训、中暑、发育焦虑、外婆的夏天、兄弟转会死敌、末位淘汰、夜不归寝、教练的儿子、妈妈的来信、冬训地狱、病房探访、跨年夜、压岁钱、技术定型危机、想放弃的夜晚、国青来信……其中 12 条戏剧事件全部手工登记 <code>EV_KIND_OVERRIDE</code>。</p>
<h3>验收数据（SIM_AGE=15 青训起步，30 生涯 / 120 青训赛季实测）</h3>
<div class="tw"><table>
<tr><th>指标</th><th>结果</th><th>验收线</th></tr>
<tr><td>青训段（15~18 岁）4 年窗口事件重复率</td><td><b>0.0%</b>（0/693）</td><td>&lt;5% ✓</td></tr>
<tr><td>池事件数</td><td><b>21 条/池</b>（11+10）</td><td>≥20 ✓</td></tr>
<tr><td>青训段戏剧占比</td><td><b>49.4%</b></td><td>—</td></tr>
<tr><td>15 岁起步模拟</td><td>30 生涯全部成功</td><td>—</td></tr>
</table></div>
<h3>工程面</h3>
<ul>
<li><code>sim_pacing.js</code> 支持 <code>SIM_AGE</code>（15 岁青训起步）/<code>SIM_ONE</code>（单生涯）参数；</li>
<li>新增 <code>test_r2.js</code>（15 断言：池规模/戏剧密度/题材广度/override/SIM_AGE 支持）；</li>
<li><code>tools/build_all.py</code> 重建（现 20 步）与仓库成品<b>逐字节一致</b>。</li>
</ul>
</div>
<h2 id="v4160">'''
s = s.replace('<h2 id="v4160">', entry, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('html done')

# ── 测试常量 ──
p = 'tools/test_changelog_page.js'
s = io.open(p, encoding='utf-8').read()
s = s.replace('secs.length === 30', 'secs.length === 31')
s = s.replace("kOf('v4.16.0') === 'play', kOf('v4.16.0'));",
              "kOf('v4.16.0') === 'play', kOf('v4.16.0'));\n  check('v4.17.0（青训补强）→ 玩法', kOf('v4.17.0') === 'play', kOf('v4.17.0'));", 1)
s = s.replace("/v4\\.16\\.0/.test(h.querySelector('.vpill').textContent)",
              "/v4\\.17\\.0/.test(h.querySelector('.vpill').textContent)")
s = s.replace("vt.indexOf('v4.16.0') < 0", "vt.indexOf('v4.17.0') < 0")
s = s.replace('chips.length === 31', 'chips.length === 32')
s = s.replace('verChips.length === 30', 'verChips.length === 31')
s = s.replace('collapsed.length === 30 - 5', 'collapsed.length === 31 - 5')
s = s.replace("'v4.16.0', 'v4.15.1'", "'v4.17.0', 'v4.16.0', 'v4.15.1'")
s = s.replace('卡片数量未变（32 个）', '卡片数量未变（33 个）')
s = s.replace(".card').length === 32", ".card').length === 33")
s = s.replace('目录芯片被搬进工具条（30 版 + 附录）', '目录芯片被搬进工具条（31 版 + 附录）')
io.open(p, 'w', encoding='utf-8').write(s)
print('constants done')

# ── 开发计划 ──
p = '开发计划.md'
s = io.open(p, encoding='utf-8').read()
s = s.replace('### R2 · 青训体验补强（1 单元）❓',
              '### R2 · 青训体验补强（✅ v4.17.0 已交付，青训段 4 年重复率 0.0%）')
io.open(p, 'w', encoding='utf-8').write(s)
print('plan done')
