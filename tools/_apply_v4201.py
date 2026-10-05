# -*- coding: utf-8 -*-
"""写 v4.20.1 更新日志（md+html）+ 测试常量。"""
import io

SHA = 'd9ffb71'

# ── md ──
p = '更新日志.md'
s = io.open(p, encoding='utf-8').read()
s = s.replace('> 当前版本：**v4.20.0** · 最后更新：2026-10-05',
              '> 当前版本：**v4.20.1** · 最后更新：2026-10-05')
s = s.replace('| **v4.20.0**',
              '| **v4.20.1** | 产出对齐：玩家三项系数对齐 NPC 产线（荣誉/季 6.2→4.8） | `__SHA__` | +120 |\n| **v4.20.0**'.replace('__SHA__', SHA), 1)
entry = '''
---

## ⚖️ v4.20.1 · 产出对齐：荣誉不再「每季一大把」

**提交**：`__SHA__` · **文件**：581,058 字符（+120，相对 v4.20.0 的 580,938）

v4.20.0 遗留项（荣誉/季 6.3、目标 2~3）的落地。

### 诊断：同一把尺子，两套刻度
玩家与 NPC 共用 `shootLine`（出手→命中→得分），但**期望分系数不同档**：

| 数据（OVR 92） | 玩家公式 | NPC 顶星（实测 npcSeasonLine） | 差距 |
| :-- | :--: | :--: | :--: |
| 得分 | `o*.36-4` ≈ 29+ | **21** | +40% |
| 助攻（PG） | `o*.10+o*.10` = 18.4 | **10** | +84% |
| 篮板（内线） | `o*.08+o*.09` = 15.6 | **12** | +30% |

→ 得分王/助攻王几乎必得，荣誉每季大满贯（逐季诊断曾抓到新秀季 12 项）。

### 修复：玩家系数对齐 NPC 产线（保留主角小幅优势）
- 得分 `.36→.28`、篮板 `.08/.09→.065/.07`、助攻 `.10/.10/.03→.06/.06/.02`；
- 防守数据两边本就同源（不动）；球队总产出本就守恒（`calibrateNpc` 从本队预算扣玩家产量，不动）。

### 验收（30 生涯前后对比）
| 指标 | 调整前 | 对齐后 |
| :-- | :--: | :--: |
| **荣誉/季** | **6.20** | **4.77**（−23%） |
| 荣誉数 均值 | 125.3 | **88.9** |
| 峰值 OVR 均值 | 90.4 | 86.8 |
| 终龄 最大 | 70 | 45 |

### 剩余组合（如实说明）
4.77 里的大头是**结构性合理项**：全明星（明星每年入选，1 项）+ 最佳阵容（1 项）+
冠军/FMVP（球队层面，2 项）= 4 项基线；超出的部分集中在
**跨联赛降维打击**——95+ 的球员转会 CBA/欧洲后，联赛顶星（92 上限）已经拦不住他。
要进一步压到 2~3，需要「联赛强度分层」或「荣誉项精简」，属于设计取向问题，
留待与作者确认真实感后再动。

### 验证记录
- 验证套件 **21/21 项 · 534/534 断言**全绿（`balance` 追加 4 断言：三项系数对齐 + NPC 顶星对照档位）；
- 重建（现 27 步）与仓库成品**逐字节一致**。

---

## ⚖️ v4.20.0 · 难度重构：成神不再「随便玩玩」'''.replace('__SHA__', SHA)
s = s.replace('\n---\n\n## ⚖️ v4.20.0 · 难度重构：成神不再「随便玩玩」', entry, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('md done')

# ── html ──
p = '更新日志.html'
s = io.open(p, encoding='utf-8').read()
s = s.replace('<span class="badge">当前版本 <b>v4.20.0</b></span><span class="badge">文件 <b>580,938</b> 字符</span><span class="badge">更新 <b>36</b> 个版本</span>',
              '<span class="badge">当前版本 <b>v4.20.1</b></span><span class="badge">文件 <b>581,058</b> 字符</span><span class="badge">更新 <b>37</b> 个版本</span>')
s = s.replace('<nav class="toc"><a href="#v4200">v4.20.0</a>',
              '<nav class="toc"><a href="#v4201">v4.20.1</a><a href="#v4200">v4.20.0</a>')
s = s.replace('<tr><td><b>v4.20.0</b></td>',
              '<tr><td><b>v4.20.1</b></td><td>产出对齐：玩家三项系数对齐 NPC 产线（荣誉/季 6.2→4.8）</td><td><code>__SHA__</code></td><td>+120</td></tr>\n<tr><td><b>v4.20.0</b></td>'.replace('__SHA__', SHA), 1)
entry = '''<h2 id="v4201">⚖️ v4.20.1 · 产出对齐：荣誉不再「每季一大把」 <span class="sha">__SHA__</span></h2>
<div class="card">
<p>v4.20.0 遗留项（荣誉/季 6.3、目标 2~3）的落地。</p>
<h3>诊断：同一把尺子，两套刻度</h3>
<p>玩家与 NPC 共用 <code>shootLine</code>，但<b>期望分系数不同档</b>：</p>
<div class="tw"><table>
<tr><th>数据（OVR 92）</th><th>玩家公式</th><th>NPC 顶星（实测）</th><th>差距</th></tr>
<tr><td>得分</td><td><code>o*.36-4</code> ≈ 29+</td><td><b>21</b></td><td>+40%</td></tr>
<tr><td>助攻（PG）</td><td><code>o*.10+o*.10</code> = 18.4</td><td><b>10</b></td><td>+84%</td></tr>
<tr><td>篮板（内线）</td><td><code>o*.08+o*.09</code> = 15.6</td><td><b>12</b></td><td>+30%</td></tr>
</table></div>
<h3>修复：玩家系数对齐 NPC 产线（保留主角小幅优势）</h3>
<ul>
<li>得分 <code>.36→.28</code>、篮板 <code>.08/.09→.065/.07</code>、助攻 <code>.10/.10/.03→.06/.06/.02</code>；</li>
<li>防守数据两边本就同源（不动）；球队总产出本就守恒（<code>calibrateNpc</code> 从本队预算扣玩家产量，不动）。</li>
</ul>
<h3>验收（30 生涯前后对比）</h3>
<div class="tw"><table>
<tr><th>指标</th><th>调整前</th><th>对齐后</th></tr>
<tr><td><b>荣誉/季</b></td><td><b>6.20</b></td><td><b>4.77</b>（−23%）</td></tr>
<tr><td>荣誉数 均值</td><td>125.3</td><td><b>88.9</b></td></tr>
<tr><td>峰值 OVR 均值</td><td>90.4</td><td>86.8</td></tr>
<tr><td>终龄 最大</td><td>70</td><td>45</td></tr>
</table></div>
<h3>剩余组合（如实说明）</h3>
<p>4.77 里的大头是<b>结构性合理项</b>：全明星 + 最佳阵容 + 冠军/FMVP ≈ 4 项基线；超出部分集中在<b>跨联赛降维打击</b>——95+ 的球员转会 CBA/欧洲后，联赛顶星（92 上限）拦不住他。要进一步压到 2~3，需要「联赛强度分层」或「荣誉项精简」，属于设计取向问题，留待确认手感后再动。</p>
<h3>验证记录</h3>
<ul>
<li>验证套件 <b>21/21 项 · 534/534 断言</b>全绿（<code>balance</code> 追加 4 断言）；</li>
<li>重建（现 27 步）与仓库成品<b>逐字节一致</b>。</li>
</ul>
</div>
<h2 id="v4200">'''.replace('__SHA__', SHA)
s = s.replace('<h2 id="v4200">', entry, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('html done')

# ── 测试常量 ──
p = 'tools/test_changelog_page.js'
s = io.open(p, encoding='utf-8').read()
s = s.replace('secs.length === 36', 'secs.length === 37')
s = s.replace("kOf('v4.20.0') === 'play', kOf('v4.20.0'));",
              "kOf('v4.20.0') === 'play', kOf('v4.20.0'));\n  check('v4.20.1（产出对齐）→ 玩法', kOf('v4.20.1') === 'play', kOf('v4.20.1'));", 1)
s = s.replace("/v4\\.20\\.0/.test(h.querySelector('.vpill').textContent)",
              "/v4\\.20\\.1/.test(h.querySelector('.vpill').textContent)")
s = s.replace("vt.indexOf('v4.20.0') < 0", "vt.indexOf('v4.20.1') < 0")
s = s.replace('chips.length === 37', 'chips.length === 38')
s = s.replace('verChips.length === 36', 'verChips.length === 37')
s = s.replace('collapsed.length === 36 - 5', 'collapsed.length === 37 - 5')
s = s.replace("'v4.20.0', 'v4.19.2'", "'v4.20.1', 'v4.20.0', 'v4.19.2'")
s = s.replace('卡片数量未变（38 个）', '卡片数量未变（39 个）')
s = s.replace(".card').length === 38", ".card').length === 39")
s = s.replace("table').length === 17", "table').length === 19")
s = s.replace('表格数量未变（17 个）', '表格数量未变（19 个）')
s = s.replace('目录芯片被搬进工具条（36 版 + 附录）', '目录芯片被搬进工具条（37 版 + 附录）')
io.open(p, 'w', encoding='utf-8').write(s)
print('constants done')
