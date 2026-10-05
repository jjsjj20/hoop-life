# -*- coding: utf-8 -*-
"""v4.19.2 日志收尾：回填 md 哈希 + 写 html 版 + 常量。"""
import io

SHA = '621ebe2'

# ── md：回填哈希 ──
p = '更新日志.md'
s = io.open(p, encoding='utf-8').read()
s = s.replace('| **v4.19.2** | 修复：移动端结果页剧情可折叠（默认收起，结果直出） | `SF` |',
              '| **v4.19.2** | 修复：移动端结果页剧情可折叠（默认收起，结果直出） | `%s` |' % SHA)
s = s.replace('**提交**：SF · **文件**：580,152', '**提交**：`%s` · **文件**：580,152' % SHA)
io.open(p, 'w', encoding='utf-8').write(s)
print('md hash filled')

# ── html ──
p = '更新日志.html'
s = io.open(p, encoding='utf-8').read()
s = s.replace('<span class="badge">当前版本 <b>v4.19.1</b></span><span class="badge">文件 <b>579,642</b> 字符</span><span class="badge">更新 <b>34</b> 个版本</span>',
              '<span class="badge">当前版本 <b>v4.19.2</b></span><span class="badge">文件 <b>580,152</b> 字符</span><span class="badge">更新 <b>35</b> 个版本</span>')
s = s.replace('<nav class="toc"><a href="#v4191">v4.19.1</a>',
              '<nav class="toc"><a href="#v4192">v4.19.2</a><a href="#v4191">v4.19.1</a>')
s = s.replace('<tr><td><b>v4.19.1</b></td>',
              '<tr><td><b>v4.19.2</b></td><td>修复：移动端结果页剧情可折叠（默认收起，结果直出）</td><td><code>%s</code></td><td>+510</td></tr>\n<tr><td><b>v4.19.1</b></td>' % SHA, 1)
entry = '''<h2 id="v4192">📱 v4.19.2 · 修复：移动端结果页剧情可折叠 <span class="sha">%s</span></h2>
<div class="card">
<p>游玩反馈第四条：「结果也显示不全」。结果页会<b>重放完整剧情文本</b>再跟结果块（选项结果 / 数值变化 / 状态面板）——手机上结果信息被压在长文之下，得下滑才看得到。</p>
<h3>修复（桌面不变，仅移动端）</h3>
<ul>
<li>结果页剧情块加 <code>.sceneFold</code> + 「📖 展开剧情」开关（<code>.foldBtn</code>）；</li>
<li><b>移动端默认收起剧情</b>——选项结果与数值变化直出，一点开关即可回顾原文（文案随态切换）；</li>
<li>桌面：开关隐藏、剧情照常显示，一切照旧。</li>
</ul>
<h3>验证记录</h3>
<ul>
<li>验证套件 <b>20/20 项 · 514/514 断言</b>全部通过（<code>ui</code> 追加 7 断言：折叠块渲染 / 默认收起 / 展开与复位 / 文案切换）；</li>
<li>重建（现 24 步）与仓库成品<b>逐字节一致</b>。</li>
</ul>
</div>
<h2 id="v4191">''' % SHA
s = s.replace('<h2 id="v4191">', entry, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('html done')

# ── 测试常量 ──
p = 'tools/test_changelog_page.js'
s = io.open(p, encoding='utf-8').read()
s = s.replace('secs.length === 34', 'secs.length === 35')
s = s.replace("kOf('v4.19.1') === 'fix', kOf('v4.19.1'));",
              "kOf('v4.19.1') === 'fix', kOf('v4.19.1'));\n  check('v4.19.2（剧情折叠修复）→ 修复', kOf('v4.19.2') === 'fix', kOf('v4.19.2'));", 1)
s = s.replace("/v4\\.19\\.1/.test(h.querySelector('.vpill').textContent)",
              "/v4\\.19\\.2/.test(h.querySelector('.vpill').textContent)")
s = s.replace("vt.indexOf('v4.19.1') < 0", "vt.indexOf('v4.19.2') < 0")
s = s.replace('chips.length === 35', 'chips.length === 36')
s = s.replace('verChips.length === 34', 'verChips.length === 35')
s = s.replace('collapsed.length === 34 - 5', 'collapsed.length === 35 - 5')
s = s.replace("'v4.19.1', 'v4.19.0'", "'v4.19.2', 'v4.19.1', 'v4.19.0'")
s = s.replace('卡片数量未变（36 个）', '卡片数量未变（37 个）')
s = s.replace(".card').length === 36", ".card').length === 37")
s = s.replace('目录芯片被搬进工具条（34 版 + 附录）', '目录芯片被搬进工具条（35 版 + 附录）')
io.open(p, 'w', encoding='utf-8').write(s)
print('constants done')
