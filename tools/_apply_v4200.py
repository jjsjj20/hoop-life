# -*- coding: utf-8 -*-
"""写 v4.20.0 更新日志（md+html）+ 测试常量。"""
import io

SHA = '9b9cb5a'

# ── md ──
p = '更新日志.md'
s = io.open(p, encoding='utf-8').read()
s = s.replace('> 当前版本：**v4.19.2** · 最后更新：2026-10-05',
              '> 当前版本：**v4.20.0** · 最后更新：2026-10-05')
s = s.replace('| **v4.19.2**',
              '| **v4.20.0** | 难度重构：成长上限/NPC 强度/续战硬上限 + 荣誉与冠军校准（成神率减半） | `__SHA__` | +996 |\n| **v4.19.2**'.replace('__SHA__', SHA), 1)
entry = '''
---

## ⚖️ v4.20.0 · 难度重构：成神不再「随便玩玩」

**提交**：`__SHA__` · **文件**：580,938 字符（+996，相对 v4.19.2 的 580,152）

游玩反馈第五条：「难度太低，随便玩都可以成篮球之神」。用 30 生涯模拟做了基线实测，
三个根因一次修完：

### 基线诊断（30 生涯 / 703 赛季）
| 症状 | 基线实测 |
| :-- | :-- |
| 峰值 OVR 过高 | 均值 **90.4**（21/30 ≥90、12/30 ≥93、6/30 ≥95） |
| 荣誉通胀 | 均值 **125 项**（多数生涯每季大满贯 6+ 项；逐季诊断抓到**新秀季即 12 项**：MVP+冠军+FMVP+第六人+进步最快…） |
| 生涯长度失控 | 「继续征战」写入的 flag **从未被读取** → 实测打到 **70 岁、51 季**（设计是 41 岁终章） |

### 修复一 · 成长与上限
- `TIER_RANGE`：S{85,99}→**{82,93}**、A{70,84}→{68,82}、B/C/D 同步下调；
- `GROWTH`：向上限收敛 16%→**11%**、训练加成 8→**6**、成年超限回落 82%→**76%**。
- 效果：「到顶」更慢（光靠天赋不够）、天花板更低。

### 修复二 · 联盟要有真对手
- NPC 能力 `R.int(55,88)` → **`R.int(54,92)`**、潜力上限 96→97 ——
  之前玩家 90+ 时联盟无人能争（MVP/得分王/冠军每季大满贯的直接原因）。

### 修复三 · 续战硬上限
- 「继续征战」真正生效（每次 +1 年、**最多 3 次**），**45 岁开局强制退役**；
- 终章 41 岁起每年冬重问一次，标题与文案随年龄动态。

### 修复四 · 荣誉与冠军校准
- 玩家对球队胜率加成 `.005→.003`（冠军不再是一人之力）；
- MVP `.55/.28/.10→.42/.16/.05`、DPOY `.45/.22/.08→.36/.15/.05`；
- 第六人**非新秀才给**；最佳关键球员前 4 且大心脏 ≥88；进步最快 ≥第 2 季、排名 ≤10、概率 .25。

### 验收（30 生涯前后对比）
| 指标 | 调整前 | 调整后 |
| :-- | :--: | :--: |
| 峰值 OVR 均值 | 90.4 | **87.5** |
| 峰值 ≥90 | 21/30 | **13/30** |
| 峰值 ≥93 | 12/30 | **6/30** |
| **神级（≥93 且 有冠/MVP）** | 11/30 | **6/30** |
| 终龄 最大 | 70 | **45** |
| 荣誉数 均值 | 125.3 | **100.8** |

### 已知遗留（下一轮）
- **荣誉/季仍为 6.3**（目标 2~3）：根因是玩家场均产出与 NPC 产出口径不同档，
  顶星玩家仍能每季霸榜多项 —— 需要一轮「产出对齐」校准（不动结构，只调权重）。

### 工程
- `sim_pacing` 现在记录峰值 OVR/档位/荣誉/终龄，并支持 `SIM_OUT` 输出目录；
- **发现并清除了一个隐蔽陷阱**：`build/` 下存在过期工具副本，实际执行的一直是它
  （导致 SIM_AGE/新字段此前未生效）——已收编 `merge_sim` 到 repo/tools 并删除过期副本；
- 新增 `test_balance.js`（12 断言）、`build/diag_honors.js`（逐季荣誉诊断）、
  `build/compare_difficulty.js`（前后对比）；验证 **21/21 项 · 528/528 断言**全绿。

---

## 📱 v4.19.2 · 修复：移动端结果页剧情可折叠'''.replace('__SHA__', SHA)
s = s.replace('\n---\n\n## 📱 v4.19.2 · 修复：移动端结果页剧情可折叠', entry, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('md done')

# ── html ──
p = '更新日志.html'
s = io.open(p, encoding='utf-8').read()
s = s.replace('<span class="badge">当前版本 <b>v4.19.2</b></span><span class="badge">文件 <b>580,152</b> 字符</span><span class="badge">更新 <b>35</b> 个版本</span>',
              '<span class="badge">当前版本 <b>v4.20.0</b></span><span class="badge">文件 <b>580,938</b> 字符</span><span class="badge">更新 <b>36</b> 个版本</span>')
s = s.replace('<nav class="toc"><a href="#v4192">v4.19.2</a>',
              '<nav class="toc"><a href="#v4200">v4.20.0</a><a href="#v4192">v4.19.2</a>')
s = s.replace('<tr><td><b>v4.19.2</b></td>',
              '<tr><td><b>v4.20.0</b></td><td>难度重构：成长上限/NPC 强度/续战硬上限 + 荣誉与冠军校准（成神率减半）</td><td><code>__SHA__</code></td><td>+996</td></tr>\n<tr><td><b>v4.19.2</b></td>'.replace('__SHA__', SHA), 1)
entry = '''<h2 id="v4200">⚖️ v4.20.0 · 难度重构：成神不再「随便玩玩」 <span class="sha">__SHA__</span></h2>
<div class="card">
<p>游玩反馈第五条：「难度太低，随便玩都可以成篮球之神」。用 30 生涯模拟做了基线实测，三个根因一次修完。</p>
<h3>基线诊断（30 生涯 / 703 赛季）</h3>
<div class="tw"><table>
<tr><th>症状</th><th>基线实测</th></tr>
<tr><td>峰值 OVR 过高</td><td>均值 <b>90.4</b>（21/30 ≥90、12/30 ≥93、6/30 ≥95）</td></tr>
<tr><td>荣誉通胀</td><td>均值 <b>125 项</b>（多数生涯每季大满贯 6+ 项；逐季诊断抓到<b>新秀季即 12 项</b>）</td></tr>
<tr><td>生涯长度失控</td><td>「继续征战」flag <b>从未被读取</b> → 实测打到 <b>70 岁、51 季</b></td></tr>
</table></div>
<h3>修复一 · 成长与上限</h3>
<ul>
<li><code>TIER_RANGE</code>：S{85,99}→<b>{82,93}</b>、A{70,84}→{68,82}、B/C/D 同步下调；</li>
<li><code>GROWTH</code>：收敛 16%→<b>11%</b>、训练加成 8→<b>6</b>、成年超限回落 82%→<b>76%</b>。</li>
</ul>
<h3>修复二 · 联盟要有真对手</h3>
<p>NPC 能力 <code>R.int(55,88)</code> → <b><code>R.int(54,92)</code></b>、潜力上限 96→97——之前玩家 90+ 时联盟无人能争。</p>
<h3>修复三 · 续战硬上限</h3>
<p>「继续征战」真正生效（每次 +1 年、<b>最多 3 次</b>），<b>45 岁开局强制退役</b>；终章 41 岁起每年冬重问，标题与文案随年龄动态。</p>
<h3>修复四 · 荣誉与冠军校准</h3>
<p>玩家对球队胜率加成 <code>.005→.003</code>；MVP <code>.55/.28/.10→.42/.16/.05</code>、DPOY <code>.45/.22/.08→.36/.15/.05</code>；第六人<b>非新秀才给</b>；最佳关键球员前 4 且大心脏 ≥88；进步最快 ≥第 2 季、排名 ≤10、概率 .25。</p>
<h3>验收（30 生涯前后对比）</h3>
<div class="tw"><table>
<tr><th>指标</th><th>调整前</th><th>调整后</th></tr>
<tr><td>峰值 OVR 均值</td><td>90.4</td><td><b>87.5</b></td></tr>
<tr><td>峰值 ≥90</td><td>21/30</td><td><b>13/30</b></td></tr>
<tr><td>峰值 ≥93</td><td>12/30</td><td><b>6/30</b></td></tr>
<tr><td><b>神级（≥93 且 有冠/MVP）</b></td><td>11/30</td><td><b>6/30</b></td></tr>
<tr><td>终龄 最大</td><td>70</td><td><b>45</b></td></tr>
<tr><td>荣誉数 均值</td><td>125.3</td><td><b>100.8</b></td></tr>
</table></div>
<h3>已知遗留（下一轮）</h3>
<p><b>荣誉/季仍为 6.3</b>（目标 2~3）：根因是玩家场均产出与 NPC 产出口径不同档，顶星玩家仍能每季霸榜多项——需要一轮「产出对齐」校准。</p>
<h3>工程</h3>
<ul>
<li><code>sim_pacing</code> 记录峰值 OVR/档位/荣誉/终龄，支持 <code>SIM_OUT</code> 输出目录；</li>
<li><b>发现并清除隐蔽陷阱</b>：<code>build/</code> 下存在过期工具副本，实际执行的一直是它（导致 SIM_AGE/新字段此前未生效）；</li>
<li>新增 <code>test_balance.js</code>（12 断言）、逐季荣誉诊断与前后对比脚本；验证 <b>21/21 项 · 528/528 断言</b>全绿。</li>
</ul>
</div>
<h2 id="v4192">'''.replace('__SHA__', SHA)
s = s.replace('<h2 id="v4192">', entry, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('html done')

# ── 测试常量 ──
p = 'tools/test_changelog_page.js'
s = io.open(p, encoding='utf-8').read()
s = s.replace('secs.length === 35', 'secs.length === 36')
s = s.replace("kOf('v4.19.2') === 'fix', kOf('v4.19.2'));",
              "kOf('v4.19.2') === 'fix', kOf('v4.19.2'));\n  check('v4.20.0（难度重构）→ 工程', kOf('v4.20.0') === 'eng', kOf('v4.20.0'));", 1)
s = s.replace("/v4\\.19\\.2/.test(h.querySelector('.vpill').textContent)",
              "/v4\\.20\\.0/.test(h.querySelector('.vpill').textContent)")
s = s.replace("vt.indexOf('v4.19.2') < 0", "vt.indexOf('v4.20.0') < 0")
s = s.replace('chips.length === 36', 'chips.length === 37')
s = s.replace('verChips.length === 35', 'verChips.length === 36')
s = s.replace('collapsed.length === 35 - 5', 'collapsed.length === 36 - 5')
s = s.replace("'v4.19.2', 'v4.19.1'", "'v4.20.0', 'v4.19.2', 'v4.19.1'")
s = s.replace('卡片数量未变（37 个）', '卡片数量未变（38 个）')
s = s.replace(".card').length === 37", ".card').length === 38")
s = s.replace("table').length === 15", "table').length === 17")
s = s.replace('表格数量未变（15 个）', '表格数量未变（17 个）')
s = s.replace('目录芯片被搬进工具条（35 版 + 附录）', '目录芯片被搬进工具条（36 版 + 附录）')
io.open(p, 'w', encoding='utf-8').write(s)
print('constants done')
