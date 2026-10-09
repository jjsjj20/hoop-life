# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 47：桌面端布局重构（v5.0.0，仅电脑端 · 手机不动）

【背景】用户设计需求（6 点 · 设计稿 v3 已确认）：
  ① 左上角玩家姓名 ② 姓名右侧身高/体重/臂展/年龄 ③ 再右侧能力值 OVR——①②③ 合为顶栏一栏
  ④ 顶栏下为时间栏（章节/赛季/阶段+进度）
  ⑤ 姓名下为功能栏——所有功能平铺、放最左侧竖栏（从上往下、固定宽、不顶开主内容）
  ⑥ 其余为事件栏（剧情/选项/结果原样，场景插画照常）

【实现】
  · 单份 DOM + CSS 分端：手机渲染原 HUD/chapter/行动栏（only-m），桌面渲染新
    顶栏(dtop)/时间栏(dtime)/功能竖栏(funcbar)（only-d）——媒体断点 900px 切换。
  · funcbar 固定 118px、sticky，14 个功能按钮竖排（合并原行动栏 5 按钮 + ☰ 更多
    菜单 13 项，条件显示签位/对阵图）；桌面隐藏原行动栏非「继续」按钮与 306px 侧栏
    （其内容已并入 📊 属性/📋 档案 overlay）。
  · 场景插画/事件内容/结果页/数据面板全部原样，仅布局归位。
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


# ═══════════ 1. CSS：分端机制 + 桌面新布局 ═══════════
sub1(".actions button:active{transform:scale(.97)}",
""".actions button:active{transform:scale(.97)}
/* ── v5.0.0 桌面布局重构：左功能竖栏 + 顶栏三段 + 时间栏（only-d/only-m 分端） ── */
.only-d{display:none}
@media(min-width:900px){
  .only-m{display:none}
  .only-d{display:block}
  .dwrap{display:flex;align-items:flex-start}
  .funcbar{flex:none;width:118px;position:sticky;top:10px;max-height:calc(100vh - 24px);overflow-y:auto;
    background:rgba(18,24,38,.72);border:1px solid var(--line2);border-radius:12px;padding:10px 8px;
    display:flex;flex-direction:column;gap:5px;margin-right:14px}
  .funcbar .fbhead{font-size:10px;color:var(--dim);letter-spacing:2px;margin:0 4px 4px}
  .funcbar button{height:34px;border-radius:8px;border:1px solid var(--line2);background:var(--btn2);
    color:var(--txt4);font-size:12px;cursor:pointer;transition:border-color .16s,color .16s}
  .funcbar button:hover{border-color:#3d4a66;color:var(--txt)}
  .funcbar button.hot{color:var(--gold)}
  .funcbar button.dim{color:var(--dim)}
  .maincol{flex:1;min-width:0}
  .dtop{display:flex;align-items:stretch;border-bottom:1px solid var(--line2);
    background:linear-gradient(180deg,rgba(23,30,45,.85),rgba(23,30,45,.55));border-radius:12px 12px 0 0}
  .dtop-name{padding:12px 18px;border-right:1px solid var(--line2);display:flex;align-items:center}
  .dtop-name b{font-size:20px;font-weight:800;color:#fff;letter-spacing:1px}
  .dtop-name span{font-size:11px;color:var(--dim);margin-left:8px}
  .dtop-body{padding:10px 18px;border-right:1px solid var(--line2);display:flex;gap:16px;align-items:center}
  .dtop-body div{text-align:center}
  .dtop-body i{display:block;font-style:normal;font-size:10px;color:var(--dim);margin-bottom:1px}
  .dtop-body b{font-size:13px;color:var(--txt2)}
  .dtop-ovr{margin-left:auto;padding:8px 20px;display:flex;align-items:center;gap:14px}
  .dtop-ovrn{text-align:right}
  .dtop-ovrn i{display:block;font-style:normal;font-size:10px;color:var(--dim)}
  .dtop-ovrn b{font-size:24px;color:var(--gold)}
  .dtop-bars{width:158px}
  .dline{margin:3px 0}
  .dline span{font-size:9px;color:var(--dim)}
  .dbar{height:4px;background:var(--field);border-radius:2px;overflow:hidden}
  .dbar i{display:block;height:100%;background:linear-gradient(90deg,var(--accent),var(--gold));border-radius:2px}
  .dtime{display:flex;align-items:center;gap:10px;padding:8px 18px;flex-wrap:wrap;
    background:rgba(18,24,38,.6);border-bottom:1px solid var(--line2);border-radius:0 0 12px 12px}
  .dt-ch{color:var(--gold);font-weight:700;font-size:12px}
  .dtime span{font-size:12px;color:var(--txt2)}
  .dt-prog{flex:1;height:3px;background:var(--field);border-radius:2px;min-width:90px}
  .dt-prog i{display:block;height:100%;background:var(--accent);border-radius:2px}
  .dt-money{margin-left:auto;font-size:11px;color:var(--dim)}
  /* 桌面退役的旧元素（信息由新顶栏/时间栏/功能栏/overlay 承载） */
  .dwrap .shell{display:block}
  .dwrap .side{display:none}
  .dwrap .chapter{display:none}
  .dwrap .actions button:not(.contAct){display:none}
  .dwrap .actions{margin-top:12px;background:none}
}""", '桌面布局 CSS')

# ═══════════ 2. JS：桌面三段渲染函数 ═══════════
sub1("function chapterTitle(){",
"""/* v5.0.0 桌面端：顶栏（姓名/身体/OVR 概览）· 时间栏（章节/赛季/阶段/进度）· 功能竖栏 */
function dtopHTML(){
  const bars=[['外线',S.a.outside],['组织',S.a.play],['防守',S.a.def],['身体',S.a.ath]]
    .map(x=>'<div class="dline"><span>'+x[0]+' '+(x[1]||55)+'</span><div class="dbar"><i style="width:'+clamp(x[1]||55,2,99)+'%"></i></div></div>').join('');
  return '<div class="dtop"><div class="dtop-name"><b>'+esc(S.name)+'</b><span>🏀 '+POS[S.pos].n+'</span></div>'
    +'<div class="dtop-body">'
    +[['身高',S.height+'cm'],['体重',S.weight+'kg'],['臂展',S.wingspan+'cm'],['年龄',S.age+'岁']]
      .map(x=>'<div><i>'+x[0]+'</i><b>'+x[1]+'</b></div>').join('')
    +'</div><div class="dtop-ovr"><div class="dtop-ovrn"><i>能力值 OVR</i><b>'+ovr()+'</b></div>'
    +'<div class="dtop-bars">'+bars+'</div></div></div>';
}
function dtimeHTML(){
  const y=(S.birthYear+S.age-1)+'-'+String(S.birthYear+S.age).slice(2)+'赛季';
  const pct=clamp(Math.round(((S.stageDone||0)/(S.stageNeed||1))*100),0,100);
  const stageTxt=S.stage==='playoffs'?('🏆 季后赛 · '+PLAYOFF_WHEN):('📅 '+stageLabel(S.stage,S.stageDone||0,S.stageNeed||1)+(STAGE_PHASE[S.stage]?(' · '+STAGE_PHASE[S.stage]):''));
  return '<div class="dtime"><b class="dt-ch">第'+(S.age-14)+'章</b>'
    +'<span>'+y+' · '+chapterTitle()+'</span><span>'+stageTxt+'</span>'
    +'<div class="dt-prog"><i style="width:'+pct+'%"></i></div><span>'+pct+'%</span>'
    +'<span class="dt-money">💰 '+money(S.value)+' ｜ 💵 '+money(S.cash)+' ｜ 📄 '+esc(contractLabel())+'</span></div>';
}
function funcbarHTML(){
  const b=(t,fn,cls)=>'<button'+(cls?' class="'+cls+'"':'')+' onclick="'+fn+'">'+t+'</button>';
  let h=b('👥 阵容','showRoster()')
    +((S.league==='CBA'||S.league==='NBA'||S.league==='欧洲')?b('📊 排名','showStandings()'):'')
    +(isPro()?b('📋 签位','showPickAssets()'):'')
    +(S.bracket?b('🏆 对阵图','showBracket()'):'')
    +b('💼 财务','showMoney()')+b('🏅 成就','showCodex()')+b('📋 档案','showArchive()')
    +b('📊 属性','showAttrs()','hot')+b('🧭 倾向','showTendHelp()')+b('🔊 音效','toggleSfx()')
    +b('📤 导出','exportSave()')+b('📥 导入','openImport()')+b('💾 存档','saveNow()')
    +b('🏁 结束生涯','endNow()','dim');
  return '<div class="fbhead">功能</div>'+h;
}
function chapterTitle(){""", '桌面三段函数')

# ═══════════ 3. renderGame 重排 ═══════════
sub1("""    $('#app').innerHTML=renderTop()+`<div class="shell"><div class="main">`+head+`<div id="stage"></div><div class="actions">
     ${UI.mode==='result'?'<button class="contAct" onclick="advance()">继续 ▶</button>':''}
     <button onclick="showRoster()">👥 阵容</button>
     ${(S.league==='CBA'||S.league==='NBA'||S.league==='欧洲')?'<button onclick="showStandings()">📊 排名</button>':''}
     <button onclick="saveNow()">💾 存档</button>
     <button onclick="openMore()">☰ 更多</button></div></div>
     <aside class="side">${renderSide()}</aside></div>`;""",
"""    $('#app').innerHTML=`<div class="only-m">`+renderTop()+`</div>`
     +dtopHTML()+dtimeHTML()
     +`<div class="dwrap"><aside class="funcbar only-d">`+funcbarHTML()+`</aside><div class="shell"><div class="main">`
     +head.replace('<div class="chapter">','<div class="chapter only-m">')
     +`<div id="stage"></div><div class="actions">
     ${UI.mode==='result'?'<button class="contAct" onclick="advance()">继续 ▶</button>':''}
     <button onclick="showRoster()">👥 阵容</button>
     ${(S.league==='CBA'||S.league==='NBA'||S.league==='欧洲')?'<button onclick="showStandings()">📊 排名</button>':''}
     <button onclick="saveNow()">💾 存档</button>
     <button onclick="openMore()">☰ 更多</button></div></div></div>
     <aside class="side only-m">${renderSide()}</aside></div>`;""", 'renderGame 分端重排')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('桌面端布局重构已应用：%d -> %d 字符（%+d）' % (orig, len(s), len(s) - orig))
