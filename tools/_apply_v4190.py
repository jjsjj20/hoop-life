# -*- coding: utf-8 -*-
"""写 v4.19.0 更新日志（md+html）+ 测试常量。"""
import io

# ── 更新日志.md ──
p = '更新日志.md'
s = io.open(p, encoding='utf-8').read()
s = s.replace('> 当前版本：**v4.18.0** · 最后更新：2026-10-05',
              '> 当前版本：**v4.19.0** · 最后更新：2026-10-05')
s = s.replace('| **v4.18.0**',
              '| **v4.19.0** | 移动端布局重构：HUD 可收起 · 行动栏吸底 · 插画压缩（游玩反馈第二条） | `c2fa788` | +1,439 |\n| **v4.18.0**', 1)
entry = '''
---

## 📱 v4.19.0 · 移动端布局重构：HUD 可收起 · 行动栏吸底 · 插画压缩

**提交**：`c2fa788` · **文件**：579,093 字符（+1,439，相对 v4.18.0 的 577,654）

游玩反馈第二条「手机游玩要上下滑动因为看不全」的落地。根因：移动端竖向堆叠里
「外壳」占掉太多——顶部 HUD 常驻（sticky，含四季阶段条 + 7 个 chips 换行）、
章节行、128px 插画，加 20px 下距的行动栏落在首屏之外。

### 方案（桌面完全不变，仅 `@media(max-width:899px)`）
- **HUD 可收起**：右上角 ▴/▾ 一键收起四季阶段条与全部 chips（只留人名行），
  `localStorage` 记忆状态；收起后顶部常驻高度约减半；
- **行动栏吸底**：`sticky bottom`——5 个按钮（阵容/排名/AI/存档/☰ 更多）随时可见，
  不必滑到底；并压扁为一排（`min-width:0` / 42px 高，含 iOS 安全区 padding）；
- **插画 128→96px**，章节行 / 事件标题 / 场景与选项间距同步压缩——
  一屏多装约 150px 内容。

### 验证记录
- 验证套件 **20/20 项 · 497/497 断言**全部通过（新增 `ui` 12 断言：
  CSS 规则就位 / 收起按钮渲染 / 切换行为与 localStorage / 切换后事件不丢）；
- 重建（现 22 步）与仓库成品**逐字节一致**。

---

## ☰ v4.18.0 · 行动栏减负：15 个按钮收敛为 5（存档/导出/音效收进 ☰ 更多）'''
s = s.replace('\n---\n\n## ☰ v4.18.0 · 行动栏减负：15 个按钮收敛为 5（存档/导出/音效收进 ☰ 更多）', entry, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('md done')

# ── 更新日志.html ──
p = '更新日志.html'
s = io.open(p, encoding='utf-8').read()
s = s.replace('<span class="badge">当前版本 <b>v4.18.0</b></span><span class="badge">文件 <b>577,654</b> 字符</span><span class="badge">更新 <b>32</b> 个版本</span>',
              '<span class="badge">当前版本 <b>v4.19.0</b></span><span class="badge">文件 <b>579,093</b> 字符</span><span class="badge">更新 <b>33</b> 个版本</span>')
s = s.replace('<nav class="toc"><a href="#v4180">v4.18.0</a>',
              '<nav class="toc"><a href="#v4190">v4.19.0</a><a href="#v4180">v4.18.0</a>')
s = s.replace('<tr><td><b>v4.18.0</b></td>',
              '<tr><td><b>v4.19.0</b></td><td>移动端布局重构：HUD 可收起 · 行动栏吸底 · 插画压缩（游玩反馈第二条）</td><td><code>c2fa788</code></td><td>+1,439</td></tr>\n<tr><td><b>v4.18.0</b></td>', 1)
entry = '''<h2 id="v4190">📱 v4.19.0 · 移动端布局重构：HUD 可收起 · 行动栏吸底 · 插画压缩 <span class="sha">c2fa788</span></h2>
<div class="card">
<p>游玩反馈第二条「手机游玩要上下滑动因为看不全」的落地。根因：移动端竖向堆叠里「外壳」占掉太多——顶部 HUD 常驻（sticky，含四季阶段条 + 7 个 chips 换行）、章节行、128px 插画，加 20px 下距的行动栏落在首屏之外。</p>
<h3>方案（桌面完全不变，仅 @media(max-width:899px)）</h3>
<ul>
<li><b>HUD 可收起</b>：右上角 ▴/▾ 一键收起四季阶段条与全部 chips（只留人名行），localStorage 记忆状态；收起后顶部常驻高度约减半；</li>
<li><b>行动栏吸底</b>：sticky bottom——5 个按钮（阵容/排名/AI/存档/☰ 更多）随时可见，不必滑到底；并压扁为一排（min-width:0 / 42px 高，含 iOS 安全区 padding）；</li>
<li><b>插画 128→96px</b>，章节行 / 事件标题 / 场景与选项间距同步压缩——一屏多装约 150px 内容。</li>
</ul>
<h3>验证记录</h3>
<ul>
<li>验证套件 <b>20/20 项 · 497/497 断言</b>全部通过（新增 <code>ui</code> 12 断言：CSS 规则就位 / 收起按钮渲染 / 切换行为与 localStorage / 切换后事件不丢）；</li>
<li>重建（现 22 步）与仓库成品<b>逐字节一致</b>。</li>
</ul>
</div>
<h2 id="v4180">'''
s = s.replace('<h2 id="v4180">', entry, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('html done')

# ── 测试常量 ──
p = 'tools/test_changelog_page.js'
s = io.open(p, encoding='utf-8').read()
s = s.replace('secs.length === 32', 'secs.length === 33')
s = s.replace("kOf('v4.18.0') === 'eng', kOf('v4.18.0'));",
              "kOf('v4.18.0') === 'eng', kOf('v4.18.0'));\n  check('v4.19.0（移动端布局重构）→ 工程', kOf('v4.19.0') === 'eng', kOf('v4.19.0'));", 1)
s = s.replace("/v4\\.18\\.0/.test(h.querySelector('.vpill').textContent)",
              "/v4\\.19\\.0/.test(h.querySelector('.vpill').textContent)")
s = s.replace("vt.indexOf('v4.18.0') < 0", "vt.indexOf('v4.19.0') < 0")
s = s.replace('chips.length === 33', 'chips.length === 34')
s = s.replace('verChips.length === 32', 'verChips.length === 33')
s = s.replace('collapsed.length === 32 - 5', 'collapsed.length === 33 - 5')
s = s.replace("'v4.18.0', 'v4.17.0'", "'v4.19.0', 'v4.18.0', 'v4.17.0'")
s = s.replace('卡片数量未变（34 个）', '卡片数量未变（35 个）')
s = s.replace(".card').length === 34", ".card').length === 35")
s = s.replace('目录芯片被搬进工具条（32 版 + 附录）', '目录芯片被搬进工具条（33 版 + 附录）')
io.open(p, 'w', encoding='utf-8').write(s)
print('constants done')
