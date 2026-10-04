# -*- coding: utf-8 -*-
"""写 v4.15.1 更新日志（md+html）+ 测试常量 + 计划勾选。"""
import io

# ── 更新日志.md ──
p = '更新日志.md'
s = io.open(p, encoding='utf-8').read()
s = s.replace('> 当前版本：**v4.15.0** · 最后更新：2026-10-04',
              '> 当前版本：**v4.15.1** · 最后更新：2026-10-04')
s = s.replace('| **v4.15.0**',
              '| **v4.15.1** | 发版保障：SW 缓存哈希化（资产更新可达）· 排名 tiebreak 确定性 · ZIP 自动打包 | `a0400a7` | ±0 |\n| **v4.15.0**', 1)
entry = '''
---

## 🔧 v4.15.1 · 发版保障修复：SW 缓存哈希化 · 排名 tiebreak 确定性 · ZIP 自动打包

**提交**：`a0400a7` · **文件**：562,925 字符（±0，纯工程修复不动游戏内容）

### 修复 1：SW 缓存版本写死 → 内容哈希化（P6 引入隐患的闭环）
- 旧版 `sw.js` 的 `CACHE='hoop-life-v4.15.0'` 写死——资产内容更新（图片重采样等）不会到达老用户；
- 改为 **CACHE = 游戏 HTML 的 sha256 内容哈希（前 12 位）**：重建有任何变化即换缓存
  （老用户资产自动刷新），完全一致的重建缓存不失效。哈希计算置于全部 HTML 修改之后。

### 修复 2：并列战绩的选秀顺位每次调用随机漂移
- `standingsWorstFirst` 的 tiebreak 原先每次调用重掷随机数——同一赛季的并列顺序
  在排名面板/选秀/赛季总结之间漂移，跨赔率档位时选秀期望也随之偶然化
  （本次实测抓到：末位期望 1.25%，应为 0.5%）；
- 改为确定性排序「**实力弱者先选**」：同赛季并列顺序稳定，语义也更合理。

### 新增：`build_all.py --zip` 自动打包
- 一条命令出 ZIP 交付包（游戏+资源+manifest/sw/icons+两份日志+构建说明），
  版本号取自更新日志；本次产物 **113 项**。

### 验证记录
- 验证套件 **17/17 项 · 452/452 断言**全部通过（新增 `r1` 6 断言：
  缓存哈希联动 / 预缓存清单 / --zip / ZIP 实物 PK 头）；
- `draft_lottery` 三连跑稳定（tiebreak 修复前该断言为偶发失败）；
- 重建（现 17 步）与仓库成品**逐字节一致**。

---

## 📡 v4.15.0 · PWA 离线可玩 + 分享卡图片版（第二周期收官）'''
s = s.replace('\n---\n\n## 📡 v4.15.0 · PWA 离线可玩 + 分享卡图片版（第二周期收官）', entry, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('md done')

# ── 更新日志.html ──
p = '更新日志.html'
s = io.open(p, encoding='utf-8').read()
s = s.replace('<span class="badge">当前版本 <b>v4.15.0</b></span><span class="badge">文件 <b>562,925</b> 字符</span><span class="badge">更新 <b>28</b> 个版本</span>',
              '<span class="badge">当前版本 <b>v4.15.1</b></span><span class="badge">文件 <b>562,925</b> 字符</span><span class="badge">更新 <b>29</b> 个版本</span>')
s = s.replace('<nav class="toc"><a href="#v4150">v4.15.0</a>',
              '<nav class="toc"><a href="#v4151">v4.15.1</a><a href="#v4150">v4.15.0</a>')
s = s.replace('<tr><td><b>v4.15.0</b></td>',
              '<tr><td><b>v4.15.1</b></td><td>发版保障：SW 缓存哈希化（资产更新可达）· 排名 tiebreak 确定性 · ZIP 自动打包</td><td><code>a0400a7</code></td><td>±0</td></tr>\n<tr><td><b>v4.15.0</b></td>', 1)
entry = '''<h2 id="v4151">🔧 v4.15.1 · 发版保障修复：SW 缓存哈希化 · 排名 tiebreak 确定性 · ZIP 自动打包 <span class="sha">a0400a7</span></h2>
<div class="card">
<h3>修复 1：SW 缓存版本写死 → 内容哈希化（P6 引入隐患的闭环）</h3>
<p>旧版 <code>sw.js</code> 的 <code>CACHE='hoop-life-v4.15.0'</code> 写死——资产内容更新（图片重采样等）不会到达老用户。改为 <b>CACHE = 游戏 HTML 的 sha256 内容哈希（前 12 位）</b>：重建有任何变化即换缓存（老用户资产自动刷新），完全一致的重建缓存不失效。哈希计算置于全部 HTML 修改之后。</p>
<h3>修复 2：并列战绩的选秀顺位每次调用随机漂移</h3>
<p><code>standingsWorstFirst</code> 的 tiebreak 原先每次调用重掷随机数——同一赛季的并列顺序在排名面板/选秀/赛季总结之间漂移，跨赔率档位时选秀期望也随之偶然化（本次实测抓到：末位期望 1.25%，应为 0.5%）。改为确定性排序「<b>实力弱者先选</b>」：同赛季并列顺序稳定，语义也更合理。</p>
<h3>新增：build_all.py --zip 自动打包</h3>
<p>一条命令出 ZIP 交付包（游戏+资源+manifest/sw/icons+两份日志+构建说明），版本号取自更新日志；本次产物 <b>113 项</b>。</p>
<h3>验证记录</h3>
<ul>
<li>验证套件 <b>17/17 项 · 452/452 断言</b>全部通过（新增 <code>r1</code> 6 断言：缓存哈希联动 / 预缓存清单 / --zip / ZIP 实物 PK 头）；</li>
<li><code>draft_lottery</code> 三连跑稳定（tiebreak 修复前该断言为偶发失败）；</li>
<li>重建（现 17 步）与仓库成品<b>逐字节一致</b>。</li>
</ul>
</div>
<h2 id="v4150">'''
s = s.replace('<h2 id="v4150">', entry, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('html done')

# ── 测试常量 ──
p = 'tools/test_changelog_page.js'
s = io.open(p, encoding='utf-8').read()
s = s.replace('secs.length === 28', 'secs.length === 29')
s = s.replace("kOf('v4.15.0') === 'art', kOf('v4.15.0'));",
              "kOf('v4.15.0') === 'art', kOf('v4.15.0'));\n  check('v4.15.1（发版保障修复）→ 修复', kOf('v4.15.1') === 'fix', kOf('v4.15.1'));", 1)
s = s.replace("/v4\\.15\\.0/.test(h.querySelector('.vpill').textContent)",
              "/v4\\.15\\.1/.test(h.querySelector('.vpill').textContent)")
s = s.replace("vt.indexOf('v4.15.0') < 0", "vt.indexOf('v4.15.1') < 0")
s = s.replace('chips.length === 29', 'chips.length === 30')
s = s.replace('verChips.length === 28', 'verChips.length === 29')
s = s.replace('collapsed.length === 28 - 5', 'collapsed.length === 29 - 5')
s = s.replace("'v4.15.0', 'v4.14.0'", "'v4.15.1', 'v4.15.0', 'v4.14.0'")
s = s.replace('卡片数量未变（30 个）', '卡片数量未变（31 个）')
s = s.replace(".card').length === 30", ".card').length === 31")
s = s.replace('目录芯片被搬进工具条（28 版 + 附录）', '目录芯片被搬进工具条（29 版 + 附录）')
io.open(p, 'w', encoding='utf-8').write(s)
print('constants done')

# ── 开发计划 ──
p = '开发计划.md'
s = io.open(p, encoding='utf-8').read()
s = s.replace('### R1 · 发版保障：SW 缓存版本自动化 + ZIP 自动打包（0.3 单元）❓ 建议必做',
              '### R1 · 发版保障：SW 缓存版本自动化 + ZIP 自动打包（✅ v4.15.1 已交付）')
s = s.replace('| 🟠 | **SW 缓存版本未自动化** | `sw.js` 的 `CACHE=\'hoop-life-v4.15.0\'` 是写死的——资产内容更新（如图片重采样）不会到达老用户，直到有人手动改版本号。HTML 本身是网络优先不受影响，但这是 P6 引入的真实隐患 | → R1 |',
              '| ✅ 已闭环 | **SW 缓存版本未自动化** | v4.15.1 改为内容哈希缓存名：重建有任何变化即换缓存，老用户资产自动刷新 |')
io.open(p, 'w', encoding='utf-8').write(s)
print('plan done')
