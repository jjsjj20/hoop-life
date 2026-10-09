# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 41：生涯档案页 2K 式收敛（v4.28.2）

【背景】用户反馈「档案也改一下」。档案页存在两个问题：
  1. 技能区 15 项逐条平铺（与「📊 属性」面板功能重复，又长又挤）；
  2. 能力雷达的右侧列表硬编码 11 项技能——v4.28.0 扩到 15 项后漏了
     罚球/抢断/力量/速度（雷达 SVG 本身表驱动已自动适配，只有列表没跟上）。

【改动】
  1. 技能区改为「六大项概览」：内线得分/外线投篮/组织传球/防守/篮板/身体素质
     各一条色条+数值（与结果页 skillLine、📊 属性同口径），并指引明细入口。
  2. 雷达列表改 SKILLS 表驱动（15 项自动，顶尖/优秀/短板 tag 保留）。
  边界：档案页其余区块（生涯数据/曲线/宿敌/更衣室/伤病/财务/荣誉/大事记）不动。
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


# ═══════════ 1. 技能区：15 项平铺 → 六大项概览 ═══════════
sub1("""  SKILLS.forEach(([k,n])=>{h+=`<label style="display:flex;justify-content:space-between;margin:10px 0 2px"><span>${n}</span><b style="color:#fff">${S.skills[k]}</b></label><div class="bar"><i style="width:${S.skills[k]}%;background:${barColor(S.skills[k])}"></i></div>`;});""",
"""  /* v4.28.2：六大项概览（2K 式，与结果页/📊 属性同口径）——15 项明细在 ☰ 更多 · 📊 属性 */
  syncFromSkills();
  const ARC=[['inside','内线得分'],['outside','外线投篮'],['play','组织传球'],['def','防守'],['reb','篮板'],['ath','身体素质']];
  ARC.forEach(([k,n])=>{const v=S.a[k]||0;h+=`<label style="display:flex;justify-content:space-between;margin:10px 0 2px"><span>${n}</span><b style="color:#fff">${v}</b></label><div class="bar"><i style="width:${v}%;background:${barColor(v)}"></i></div>`;});
  h+=`<div class="mini" style="margin:6px 0 0">15 项细分属性（罚球/抢断/力量/速度…）→ ☰ 更多 · 📊 属性 查看。</div>`;""", '技能区六大项概览')

# ═══════════ 2. 雷达列表：硬编码 11 项 → SKILLS 表驱动 15 项 ═══════════
sub1("""  h+=`<label>🕸 能力雷达（11 项）</label><div class="radwrap">
   <div class="radcol">${radarSVG(280,240,true)}</div>
   <div class="listcol">${['three','mid','finish','dunk','handle','pass','perdef','intdef','block','reb','clutch']
     .map(k=>{const nm=(SKILLS.find(s=>s[0]===k)||[k,k])[1],v=S.skills[k];
       const tag=v>=85?'<span class="gold">顶尖</span>':v>=70?'<span class="up">优秀</span>':v>=55?'':'<span class="down">短板</span>';
       return `<i>${nm}</i><b>${v}</b> ${tag}`;}).join('<br>')}</div></div>`;""",
"""  h+=`<label>🕸 能力雷达（15 项）</label><div class="radwrap">
   <div class="radcol">${radarSVG(280,240,true)}</div>
   <div class="listcol">${SKILLS.map(([k,nm])=>{const v=S.skills[k];
       const tag=v>=85?'<span class="gold">顶尖</span>':v>=70?'<span class="up">优秀</span>':v>=55?'':'<span class="down">短板</span>';
       return `<i>${nm}</i><b>${v}</b> ${tag}`;}).join('<br>')}</div></div>`;""", '雷达列表 15 项')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('生涯档案页 2K 式收敛已应用：%d -> %d 字符（%+d）' % (orig, len(s), len(s) - orig))
