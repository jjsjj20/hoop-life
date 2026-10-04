# -*- coding: utf-8 -*-
"""写 v4.16.0 更新日志（md+html）+ 测试常量 + 计划勾选 R3。"""
import io

# ── 更新日志.md ──
p = '更新日志.md'
s = io.open(p, encoding='utf-8').read()
s = s.replace('> 当前版本：**v4.15.1** · 最后更新：2026-10-04',
              '> 当前版本：**v4.16.0** · 最后更新：2026-10-04')
s = s.replace('| **v4.15.1**',
              '| **v4.16.0** | R3 摆烂机制实装：默许摆烂 → 胜率 −10pp + 结算文案（叙事变机制） | `449e0b4` | +1,324 |\n| **v4.15.1**', 1)
entry = '''
---

## ⚖️ v4.16.0 · R3 摆烂机制实装（叙事变机制）

**提交**：`449e0b4` · **文件**：563,786 字符（+746，相对 v4.15.1 的 563,040）

v4.14.0 的「管理层的暗示」只是叙事抉择——接受后战绩没有任何真实反馈。本版把它变成机制：

- **默许摆烂写入 `S.flags.tankYear`**（=当前生涯年）→ `computeStandings`
  对摆烂球队施加 **wpc −0.10**（10 个百分点，验收线 ≥5）——排名面板/选秀顺位/赛季总结同源生效；
- **接受时排名缓存立即失效**（`S._stCache={}`），惩罚不被旧缓存吞掉；
- **跨年自动过期**：`tankYear` 只匹配当前生涯年，nextYear 之后想再摆得再谈一次；
- **赛季结算文案**：`res.tankNote`「管理层按下了计时器——这一年的战绩，为未来签位让了路」，
  renderSeason 以红字展示；
- **签位闭环**：摆烂 → 我队槽位更差（战绩最差排最前）→ 落入保护区 →
  选秀夜签位触保回退（v4.11 机制自然兑现）。

### 验收数据（20 次重算均值，统计断言）
| 指标 | 结果 | 验收线 |
|:--|:--:|:--:|
| 接受摆烂后同年预期胜率下降 | **10.0pp** | ≥5pp ✓ |
| 跨年自动过期 | ✓ | — |
| 排名缓存失效（惩罚立即生效） | ✓ | — |

### 工程面：SW 缓存名收口
新增构建步骤⑱ `patch_sw_cache.py`：`sw.js` 的 CACHE 名由**最终 HTML 的内容哈希**覆写
（此前 patch_pwa 在中途计算，后续步骤再改 HTML 会造成缓存名与产物不一致——R1 验收抓到）。
`patch_pwa.py` 的 CACHE 改为占位 `hoop-life-DEV`。此后无论新增多少构建步骤，SW 缓存名永远与产物一致。

### 验证记录
- 验证套件 **18/18 项 · 461/461 断言**全部通过（新增 `r3` 7 断言）；
- `tools/build_all.py` 重建（现 19 步）与仓库成品**逐字节一致**。

---

## 🔧 v4.15.1 · 发版保障修复：SW 缓存哈希化 · 排名 tiebreak 确定性 · ZIP 自动打包'''
s = s.replace('\n---\n\n## 🔧 v4.15.1 · 发版保障修复：SW 缓存哈希化 · 排名 tiebreak 确定性 · ZIP 自动打包', entry, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('md done')

# ── 更新日志.html ──
p = '更新日志.html'
s = io.open(p, encoding='utf-8').read()
s = s.replace('<span class="badge">当前版本 <b>v4.15.1</b></span><span class="badge">文件 <b>562,925</b> 字符</span><span class="badge">更新 <b>29</b> 个版本</span>',
              '<span class="badge">当前版本 <b>v4.16.0</b></span><span class="badge">文件 <b>563,786</b> 字符</span><span class="badge">更新 <b>30</b> 个版本</span>')
s = s.replace('<nav class="toc"><a href="#v4151">v4.15.1</a>',
              '<nav class="toc"><a href="#v4160">v4.16.0</a><a href="#v4151">v4.15.1</a>')
s = s.replace('<tr><td><b>v4.15.1</b></td>',
              '<tr><td><b>v4.16.0</b></td><td>R3 摆烂机制实装：默许摆烂 → 胜率 −10pp + 结算文案（叙事变机制）</td><td><code>449e0b4</code></td><td>+746</td></tr>\n<tr><td><b>v4.15.1</b></td>', 1)
entry = '''<h2 id="v4160">⚖️ v4.16.0 · R3 摆烂机制实装（叙事变机制） <span class="sha">449e0b4</span></h2>
<div class="card">
<p>v4.14.0 的「管理层的暗示」只是叙事抉择——接受后战绩没有任何真实反馈。本版把它变成机制：</p>
<ul>
<li><b>默许摆烂写入 <code>S.flags.tankYear</code></b>（=当前生涯年）→ <code>computeStandings</code> 对摆烂球队施加 <b>wpc −0.10</b>（10 个百分点，验收线 ≥5）——排名面板/选秀顺位/赛季总结同源生效；</li>
<li><b>接受时排名缓存立即失效</b>（<code>S._stCache={}</code>），惩罚不被旧缓存吞掉；</li>
<li><b>跨年自动过期</b>：<code>tankYear</code> 只匹配当前生涯年，nextYear 之后想再摆得再谈一次；</li>
<li><b>赛季结算文案</b>：<code>res.tankNote</code>「管理层按下了计时器——这一年的战绩，为未来签位让了路」，renderSeason 以红字展示；</li>
<li><b>签位闭环</b>：摆烂 → 我队槽位更差（战绩最差排最前）→ 落入保护区 → 选秀夜签位触保回退（v4.11 机制自然兑现）。</li>
</ul>
<h3>验收数据（20 次重算均值，统计断言）</h3>
<div class="tw"><table>
<tr><th>指标</th><th>结果</th><th>验收线</th></tr>
<tr><td>接受摆烂后同年预期胜率下降</td><td><b>10.0pp</b></td><td>≥5pp ✓</td></tr>
<tr><td>跨年自动过期</td><td>✓</td><td>—</td></tr>
<tr><td>排名缓存失效（惩罚立即生效）</td><td>✓</td><td>—</td></tr>
</table></div>
<h3>工程面：SW 缓存名收口</h3>
<p>新增构建步骤⑱ <code>patch_sw_cache.py</code>：<code>sw.js</code> 的 CACHE 名由<b>最终 HTML 的内容哈希</b>覆写（此前 patch_pwa 在中途计算，后续步骤再改 HTML 会造成缓存名与产物不一致——R1 验收抓到）。<code>patch_pwa.py</code> 的 CACHE 改为占位 <code>hoop-life-DEV</code>。此后无论新增多少构建步骤，SW 缓存名永远与产物一致。</p>
<h3>验证记录</h3>
<ul>
<li>验证套件 <b>18/18 项 · 461/461 断言</b>全部通过（新增 <code>r3</code> 7 断言）；</li>
<li><code>tools/build_all.py</code> 重建（现 19 步）与仓库成品<b>逐字节一致</b>。</li>
</ul>
</div>
<h2 id="v4151">'''
s = s.replace('<h2 id="v4151">', entry, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('html done')

# ── 测试常量 ──
p = 'tools/test_changelog_page.js'
s = io.open(p, encoding='utf-8').read()
s = s.replace('secs.length === 29', 'secs.length === 30')
s = s.replace("kOf('v4.15.1') === 'fix', kOf('v4.15.1'));",
              "kOf('v4.15.1') === 'fix', kOf('v4.15.1'));\n  check('v4.16.0（摆烂机制）→ 玩法', kOf('v4.16.0') === 'play', kOf('v4.16.0'));", 1)
s = s.replace("/v4\\.15\\.1/.test(h.querySelector('.vpill').textContent)",
              "/v4\\.16\\.0/.test(h.querySelector('.vpill').textContent)")
s = s.replace("vt.indexOf('v4.15.1') < 0", "vt.indexOf('v4.16.0') < 0")
s = s.replace('chips.length === 30', 'chips.length === 31')
s = s.replace('verChips.length === 29', 'verChips.length === 30')
s = s.replace('collapsed.length === 29 - 5', 'collapsed.length === 30 - 5')
s = s.replace("'v4.15.1', 'v4.15.0'", "'v4.16.0', 'v4.15.1', 'v4.15.0'")
s = s.replace('卡片数量未变（31 个）', '卡片数量未变（32 个）')
s = s.replace(".card').length === 31", ".card').length === 32")
s = s.replace('目录芯片被搬进工具条（29 版 + 附录）', '目录芯片被搬进工具条（30 版 + 附录）')
io.open(p, 'w', encoding='utf-8').write(s)
print('constants done')

# ── 开发计划 ──
p = '开发计划.md'
s = io.open(p, encoding='utf-8').read()
s = s.replace('### R3 · 摆烂机制实装（0.5 单元）❓',
              '### R3 · 摆烂机制实装（✅ v4.16.0 已交付，验收 10pp ≥5pp）')
s = s.replace('| ⚪ | **摆烂只有叙事没有机制** | v4.14.0 的「管理层的暗示」是纯抉择事件，接受后战绩没有任何真实反馈——"摆烂"没摆出后果 | → R3 |',
              '| ✅ 已闭环 | **摆烂只有叙事没有机制** | v4.16.0：默许摆烂 → 本季胜率 −10pp（缓存失效立即生效）+ 结算红字文案，跨年自动过期 |')
io.open(p, 'w', encoding='utf-8').write(s)
print('plan done')
