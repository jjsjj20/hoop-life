# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 19：UI 减负——行动栏 15 个按钮收敛为 5 个 + ☰ 更多菜单（v4.18.0）

游玩反馈第一条：「按钮太多了」。行动栏经 13 个版本叠加到 15 个按钮（阵容/排名/签位/
对阵图/财务/倾向/档案/成就/AI/新闻/音效/存档/导出/导入/结束），手机上要滚两屏。

整合方案（保留高频与安全项，其余进分组菜单）：
  · 行内保留 5 个：👥 阵容 · 📊 排名 · 🤖 AI · 💾 存档 · ☰ 更多
  · ☰ 更多覆盖层分三组：数据（签位/对阵图/财务/成就/档案）、
    设置与工具（倾向/新闻/音效/导出/导入）、生涯（提前结束生涯）
  · toggleSfx 的提示文案同步改指「☰ 更多」
"""
import os

BASE = os.path.dirname(os.path.abspath(__file__))
HTML = os.environ.get('GAME_HTML') or os.path.join(BASE, '..', 'output', '篮球人生.html')

s = open(HTML, encoding='utf-8').read()
orig = len(s)


def sub1(old, new, why):
    global s
    n = s.count(old)
    if n != 1:
        raise SystemExit('!! %s 匹配 %d 次（期望 1）' % (why, n))
    s = s.replace(old, new)


# ═══════════ 1. openMore 菜单（插在 endNow 之前）═══════════
sub1("""function endNow(){""",
"""/* ☰ 更多（v4.18.0）：行动栏减负——15 个按钮收敛为 5 个，次要功能集中到这个覆盖层 */
function openMore(){
  const pro=(S.league==='CBA'||S.league==='NBA'||S.league==='欧洲');
  const mb=(t,fn)=>'<button class="btn" style="flex:1 1 44%;min-width:118px" onclick="'+fn+'">'+t+'</button>';
  const data=[
    pro?mb('📋 签位','showPickAssets()'):'',
    S.bracket?mb('🏆 对阵图','showBracket()'):'',
    mb('💼 财务','showMoney()'),
    mb('🏆 成就','showCodex()'),
    mb('📋 档案','showArchive()')
  ].join('');
  const tools=[
    mb('🧭 倾向','showTendHelp()'),
    mb('📰 新闻','AI.newsOpen()'),
    mb(sfxEnabled()?'🔊 音效开':'🔇 音效关','toggleSfx()'),
    mb('📤 导出存档','exportSave()'),
    mb('📥 导入存档','openImport()')
  ].join('');
  openOvl('<h3>☰ 更多功能</h3>'
    +'<div class="mini" style="margin:10px 0 6px">数据</div>'
    +'<div style="display:flex;gap:8px;flex-wrap:wrap">'+data+'</div>'
    +'<div class="mini" style="margin:14px 0 6px">设置与工具</div>'
    +'<div style="display:flex;gap:8px;flex-wrap:wrap">'+tools+'</div>'
    +'<div class="mini" style="margin:14px 0 6px">生涯</div>'
    +'<div style="display:flex;gap:8px;flex-wrap:wrap">'+mb('🏁 提前结束生涯','endNow()')+'</div>'
    +'<button class="btn ghost" style="margin-top:16px" onclick="closeOvl()">关闭</button>');
}
function endNow(){""", 'openMore 插入')

# ═══════════ 2. 行动栏收敛为 5 个 ═══════════
sub1("""     <button onclick="showRoster()">👥 阵容</button>
     ${(S.league==='CBA'||S.league==='NBA'||S.league==='欧洲')?'<button onclick="showStandings()">📊 排名</button><button onclick="showPickAssets()">📋 签位</button>':''}
     ${S.bracket?'<button onclick="showBracket()">🏆 对阵图</button>':''}
     <button onclick="showMoney()">💼 财务</button><button onclick="showTendHelp()">🧭 倾向</button>
     <button onclick="showArchive()">📋 档案</button>
    <button onclick="showCodex()">🏆 成就</button>
     <button onclick="AI.openPanel()">🤖 AI</button>
     <button onclick="AI.newsOpen()">📰 新闻</button>
     <button id="sfxBtn" onclick="toggleSfx()">${sfxEnabled()?'🔊 音效':'🔇 音效'}</button>
     <button onclick="saveNow()">💾 存档</button>
     <button onclick="exportSave()">📤 导出</button>
     <button onclick="openImport()">📥 导入</button>
     <button onclick="endNow()">🏁 结束</button></div></div>""",
"""     <button onclick="showRoster()">👥 阵容</button>
     ${(S.league==='CBA'||S.league==='NBA'||S.league==='欧洲')?'<button onclick="showStandings()">📊 排名</button>':''}
     <button onclick="AI.openPanel()">🤖 AI</button>
     <button onclick="saveNow()">💾 存档</button>
     <button onclick="openMore()">☰ 更多</button></div></div>""", '行动栏收敛')

# ═══════════ 3. toggleSfx 提示文案改指「☰ 更多」═══════════
sub1("""else toast('已静音（工具条上的 🔊 按钮可以再打开）');""",
"""else toast('已静音（☰ 更多 → 🔊 音效 可以再打开）');""", '音效提示文案')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('UI 减负已应用：%d -> %d 字符（%+d）' % (orig, len(s), len(s) - orig))
