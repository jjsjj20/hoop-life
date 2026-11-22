# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 51：界面层级与响应式精修（v5.0.5）

末尾统一样式覆盖，修复移动端重复顶栏和主操作样式冲突；
整理首页入口、桌面功能导航、事件决策与结果反馈，不改数值和存档格式。
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


def section(start, end, new, why):
    if s.count(start) != 1 or s.count(end) != 1:
        raise SystemExit('!! %s 区块边界不唯一' % why)
    a, b = s.index(start), s.index(end)
    if b <= a:
        raise SystemExit('!! %s 区块顺序异常' % why)
    sub1(s[a:b], new, why)


# 所有旧样式之后统一覆盖，避免早期移动断点被后面的组件基础规则覆盖。
sub1('</head>\n<body>\n<div id="app"></div>', r'''<style id="ui-polish">
/* ── v5.0.5：生涯界面精修 ── */
.dtop,.dtime{display:none}
/* 首页：球场封面、清晰的主入口与独立存档管理 */
.home{padding-top:28px}
.home-brand{display:flex;justify-content:space-between;align-items:center;margin:0 2px 14px;
  color:var(--txt4);font-size:12px;letter-spacing:1px}
.home-brand b{color:var(--txt2);font-weight:800;letter-spacing:2px}
.home-brand b::before{content:'';display:inline-block;width:8px;height:8px;margin-right:9px;
  border-radius:50%;background:var(--accent);box-shadow:0 0 14px rgba(249,115,22,.4)}
.home .hero{padding:0}
.home .heroArt{height:300px;border-radius:20px}
.home .heroArt img{object-position:65% 62%;filter:brightness(.9) saturate(.85)}
.home .heroTx{inset:0;padding:36px 38px;text-align:left;display:flex;flex-direction:column;align-items:flex-start;
  justify-content:center;background:linear-gradient(90deg,rgba(6,10,17,.94),rgba(6,10,17,.67) 42%,rgba(6,10,17,.06) 82%)}
.home-eyebrow{font-size:11px;letter-spacing:3px;color:var(--accent-txt);font-weight:700}
.home .hero h1{margin:10px 0;font-size:46px;line-height:1.2;letter-spacing:6px;color:#fff;
  background:none;filter:none}
.home .hero .sub{font-size:15px;color:#d4dce9;line-height:1.8}
.home-route{display:flex;align-items:center;gap:10px;margin-top:24px;font-size:11px;color:#c3cad8}
.home-route i{font-style:normal;color:var(--accent)}
.home-grid{display:grid;grid-template-columns:minmax(0,1.3fr) minmax(0,1fr);gap:18px;margin-top:20px}
.home .home-save{margin:0;padding:24px;border-radius:18px;min-width:0}
.home-kicker{font-size:11px;letter-spacing:1.4px;color:var(--accent-txt);font-weight:700;margin-bottom:10px}
.home-save h2{font-size:23px;line-height:1.4;letter-spacing:.5px;margin:0 0 8px;overflow-wrap:anywhere}
.home-save .mini{margin-top:6px;color:var(--txt4)}
.home-save .btn{margin:20px 0 0;font-size:15px;height:50px}
.home-save .btn.ghost{margin-top:10px}
.home-save .minibtn{min-height:40px}
.save-meta{display:flex;flex-wrap:wrap;gap:6px;margin-top:14px}
.save-meta span{padding:3px 9px;border:1px solid var(--line2);border-radius:6px;font-size:11px;color:var(--txt3)}
.save-tools{margin-top:18px;border-top:1px solid var(--line);padding-top:12px}
.save-tools summary{cursor:pointer;color:var(--txt4);font-size:12px;line-height:30px}
.save-tools .danger{color:#fca5a5;border-color:rgba(248,113,113,.3)}
.home-note{padding:22px 24px;border:1px solid var(--line3);border-radius:18px;background:rgba(13,18,30,.55)}
.home-note h2{margin:0 0 16px;font-size:13px;font-weight:700;color:var(--txt2)}
.home-step{display:grid;grid-template-columns:26px 1fr;gap:12px;margin-top:18px}
.home-step>span{color:var(--accent-txt);font-size:11px;letter-spacing:1px;padding-top:2px}
.home-step b{font-size:13px;color:var(--txt3);font-weight:600}
.home-step p{margin:3px 0 0;color:var(--muted);font-size:12px;line-height:1.75}
.home-footer{font-size:11px;color:var(--muted);text-align:center;margin:20px 0 0;letter-spacing:1px}
/* 剧情与决策：阅读宽度、段落节奏和可比较的选项 */
#stage .etitle{margin:4px 0 16px;line-height:1.5;letter-spacing:.5px}
#stage .scene{line-height:1.85;color:#d9dfeb;box-shadow:var(--inner);background:#111827}
#stage .scene p:first-child{font-size:inherit;color:var(--txt2)}
.decision-head{display:flex;align-items:center;justify-content:space-between;gap:12px;margin:24px 0 12px}
.decision-head h2{font-size:13px;letter-spacing:1px;font-weight:700;margin:0;color:var(--txt2)}
.decision-head>span{font-size:11px;color:var(--muted)}
#chs{display:grid;gap:10px}
#chs .ch{margin:0;min-height:62px;padding:16px;background:#161f30;border-color:#2b374d;box-shadow:none}
#chs .ch .idx{width:26px;height:26px;border-radius:8px;background:#243046;color:#b9c6da}
#chs .ch .ctext{padding-top:2px;overflow-wrap:anywhere}
#chs .ch:hover,#chs .ch.kbsel{border-color:var(--accent);background:#222a38;transform:translateY(-1px);
  box-shadow:0 0 0 1px rgba(249,115,22,.12)}
#chs .ch:hover .idx,#chs .ch.kbsel .idx{background:var(--accent);color:#fff}
#chs .mini{margin-top:4px;font-size:11px;line-height:1.7}
#chs>.btn.ghost.small{margin:0;height:40px;font-size:12px;background:transparent;border-style:dashed;color:var(--muted)}
#chs>.btn.ghost.small:hover{color:var(--txt2)}
/* 结果：选择回顾、叙事、变化与可展开状态 */
.result{padding:20px 22px;box-shadow:var(--inner)}
.result-choice{display:flex;flex-direction:column;gap:5px;margin-bottom:16px;padding-bottom:14px;border-bottom:1px solid var(--line)}
.result-choice span{font-size:11px;letter-spacing:1.2px;color:var(--accent-txt)}
.result-choice b{font-size:14px;font-weight:600;line-height:1.7;color:var(--txt2)}
.result .out{font-size:15px;line-height:1.85;margin:0 0 16px}
.result .out p{margin:0 0 12px}.result .out p:last-child{margin:0}
.result .gain{padding:5px 11px;border-radius:8px}
.result-status{border-top:1px solid var(--line);margin-top:16px;padding-top:8px}
.result-status summary{cursor:pointer;font-size:12px;color:var(--txt4);padding:8px 0;min-height:40px}
.result-status .panel{padding:8px 0}
.result-status .kv i{color:var(--muted)}
/* 功能页始终提供回到事件的入口，长页滚动时也能操作。 */
.funcnav{position:sticky;top:10px;z-index:6;display:flex;align-items:center;gap:8px;padding:8px;
  margin:0 0 16px;border:1px solid var(--line2);border-radius:12px;background:var(--card2);box-shadow:var(--shadow-sm)}
.funcnav button{min-height:40px;padding:8px 14px;border:1px solid var(--line2);border-radius:8px;
  background:var(--btn);color:var(--txt3);font:inherit;font-size:12px;cursor:pointer}
.funcnav .func-return{color:var(--accent-txt);background:rgba(249,115,22,.1);border-color:rgba(249,115,22,.3)}
.funcnav button:hover{background:var(--btn-hot)}
/* 弹层的关闭入口始终可点 */
.ovl .x{position:sticky;top:0;z-index:2;width:44px;height:44px;border-radius:10px;background:var(--btn2);color:var(--txt3)}
@media(min-width:900px){
  #app{padding-top:24px}
  .home{padding-top:8px;max-width:960px;margin:0 auto}
  .dtop{display:flex;border:1px solid var(--line2);border-bottom:0;border-radius:16px 16px 0 0}
  .dtop-name{padding:16px 22px;flex-wrap:wrap;gap:4px}
  .dtop-name span{font-size:12px;color:var(--txt4);margin-left:0;flex-basis:100%}
  .dtop-body i,.dtop-ovrn i{font-size:11px;color:var(--txt4)}
  .dtop-body b{font-size:14px}
  .dtop-ovrn b{font-size:30px;line-height:1.2}
  .dline span{font-size:10px;color:var(--txt4)}
  .dtime{display:flex;gap:10px;padding:11px 20px;border:1px solid var(--line2);border-radius:0 0 16px 16px}
  .dtime .dt-money{font-size:11px;color:var(--txt4)}
  .dwrap{gap:24px;margin-top:22px}
  .dwrap>.shell{flex:1;min-width:0;display:block}
  .dwrap .main{width:100%;min-width:0}
  .funcbar{width:144px;margin-right:0;padding:12px 10px;border-radius:14px;gap:5px;background:rgba(16,23,37,.8)}
  .funcbar .fbhead{font-size:10px;letter-spacing:1px;color:var(--muted);margin:14px 8px 4px}
  .funcbar .fbhead:first-child{margin-top:2px}
  .funcbar button{position:relative;min-height:38px;flex-shrink:0;height:auto;text-align:left;padding:9px 10px;
    border-color:transparent;background:transparent;color:var(--txt4);font-size:12px}
  .funcbar button:hover{background:#1c2638;border-color:#2b374d;color:#fff}
  .funcbar button.on{color:var(--accent-txt);background:rgba(249,115,22,.1);border-color:rgba(249,115,22,.3)}
  .funcbar button.on::before{content:'';position:absolute;left:-11px;top:10px;bottom:10px;width:3px;border-radius:3px;background:var(--accent)}
  .funcbar button.dim{margin-top:10px;border-top:1px solid var(--line);border-radius:0;color:#b9989d}
  #stage>.art:not(.sm){height:156px;margin-bottom:20px}
  #stage>.scene{padding:22px 26px;font-size:15.5px}
  #stage>.etitle{font-size:24px}
}
@media(max-width:899px){
  #app{padding-bottom:calc(24px + env(safe-area-inset-bottom))}
  .home{padding-top:18px}
  .home-brand{font-size:10px;margin-bottom:12px}
  .home .heroArt{height:218px;border-radius:16px}
  .home .heroTx{padding:24px}
  .home .hero h1{font-size:34px;letter-spacing:4px;margin:10px 0}
  .home .hero .sub{font-size:12px}
  .home-route{font-size:10px;gap:8px;margin-top:20px}
  .home-eyebrow{font-size:9px;letter-spacing:2px}
  .home-grid{grid-template-columns:1fr;gap:12px;margin-top:14px}
  .home .home-save{padding:20px}
  .home-save h2{font-size:20px}
  .home-note{padding:18px 20px}
  .home-note h2{margin-bottom:10px}
  .home-step{margin-top:12px}
  .home-footer{font-size:10px;letter-spacing:.5px;margin-top:16px}
  .hudmin{min-width:36px;width:36px;height:36px}
  #stage .etitle{font-size:20px;margin-bottom:12px}
  #stage .scene{padding:16px 17px 16px 20px;font-size:15px;line-height:1.8}
  .decision-head{margin:20px 0 10px}
  #chs{gap:9px}
  #chs .ch{display:grid;grid-template-columns:26px minmax(0,1fr);column-gap:10px;row-gap:6px;min-height:56px;padding:13px}
  #chs .ch .idx{grid-column:1;grid-row:1;margin-top:1px}
  #chs .ch .ctext{grid-column:2;grid-row:1;font-size:15px}
  #chs .ch .ctag{grid-column:2;justify-self:start;white-space:normal;max-width:100%;font-size:11px}
  .actions{gap:6px;margin-top:14px;padding-top:10px}
  .actions button{min-width:0;min-height:44px;height:44px;padding:0 5px;font-size:12px}
  .actions button.contAct,.actions button.contAct:hover{display:block;order:-1;flex:1.4;min-height:44px;height:44px;
    background:linear-gradient(135deg,#fb923c,#ea580c);border-color:#fb923c;color:#fff;font-weight:800;
    box-shadow:0 8px 22px -12px rgba(249,115,22,.8)}
  .result{padding:17px 18px}
  .ovl .box,.ovl .box.mid,.ovl .box.wide{width:calc(100% - 20px);margin:10px auto;max-height:calc(100dvh - 20px);
    overflow-y:auto;overscroll-behavior:contain;padding:14px;border-radius:16px}
}
@media(max-width:360px){
  .home .heroArt{height:202px}.home .heroTx{padding:20px}.home .hero h1{font-size:30px}
  .home-route{gap:6px}.home-brand{letter-spacing:.5px}
  .actions:has(.contAct){display:grid;grid-template-columns:repeat(3,minmax(0,1fr))}
  .actions:has(.contAct) .contAct{grid-column:1/-1;grid-row:1}
}
@media(prefers-reduced-motion:reduce){
  #stage>*,.art{animation:none!important}#chs .ch,#chs .ch .ctext{transition:none;transform:none}
}
</style>
</head>
<body>
<div id="app"></div>''', '末尾界面精修样式')

section('function renderMenu(){', '/* ---- 10.1b 游戏模式选择 ---- */', r'''function renderMenu(){
  const d=load(),has=d&&d.name;
  let ab=null;try{const tb=JSON.parse(localStorage.getItem(CFG.SAVE_KEY+'.autobak')||'null');ab=(tb&&tb.S)?tb.S:null;}catch(_){}
  $('#app').innerHTML=`<main class="home">
   <div class="home-brand"><b>HOOP LIFE</b><span>篮球生涯模拟</span></div>
   <div class="hero"><div class="heroArt">
    <img src="assets/art/hero.webp" alt="灯光下的篮球场" decoding="async" fetchpriority="high">
    <div class="heroTx"><div class="home-eyebrow">YOUR CAREER. YOUR STORY.</div>
     <h1>篮球人生</h1><div class="sub">每一次选择，都写进你的生涯。</div>
     <div class="home-route"><span>青训起步</span><i>→</i><span>职业征程</span><i>→</i><span>荣誉之路</span></div>
    </div>
   </div></div>
   <div class="home-grid">
    <section class="card slot home-save" aria-label="生涯入口">${has?`
     <div class="home-kicker">继续未完的故事</div>
     <h2>${esc(d.name)} <span style="font-size:13px;color:var(--txt4);font-weight:400">${d.age}岁 · ${esc((POS[d.pos]||{}).n||'未知位置')}</span></h2>
     <div class="mini">${esc(d.team||'待定')} · ${esc(LEAGUE_NAMES[d.league]||'未知联赛')}</div>
     <div class="save-meta"><span>OVR ${(d.a&&d.pos)?ovrOf(d):'—'}</span><span>身价 ${money(d.value||0)}</span><span>${d.mode==='fast'?'⚡ 快速模式':'📖 沉浸模式'}</span></div>
     <button class="btn" onclick="continueGame()">📂 读取存档，继续生涯</button>
     <button class="btn ghost" onclick="renderModeSelect()">开启新的生涯</button>
     <details class="save-tools"><summary>管理存档</summary>
      <button class="minibtn" onclick="exportSave()">📤 导出存档（存成文件随身带走）</button>
      <button class="minibtn" onclick="openImport()">📥 导入存档（从文件或文本恢复）</button>
      <button class="minibtn danger" onclick="delSave()">🗑 清除存档</button>
     </details>
    `:`
     <div class="home-kicker">你的生涯，即将开场</div><h2>从第一声哨响开始</h2>
     <div class="mini">创建你的球员，在训练、比赛与人生之间做出选择，走出属于自己的职业道路。</div>
     ${ab?`<div class="mini">🛟 检测到自动备份：${esc(ab.name||'未知')} · ${ab.age||'?'}岁 · ${esc(ab.team||'待定')}</div><button class="btn" onclick="recoverAutobak()">♻ 恢复自动备份，继续生涯</button><button class="btn ghost" onclick="renderModeSelect()">🎮 开始游戏</button>`:`<button class="btn" onclick="renderModeSelect()">🎮 开始游戏</button>`}
     <button class="minibtn" onclick="openImport()">📥 已有存档文件？从这里导入</button>
    `}</section>
    <section class="home-note" aria-label="生涯旅程"><h2>不止于球场上的胜负</h2>
     <div class="home-step"><span>01</span><div><b>塑造你的打法</b><p>从位置与能力分配开始，找到最适合自己的比赛方式。</p></div></div>
     <div class="home-step"><span>02</span><div><b>经历球员的人生</b><p>训练、合同、转会与更衣室，每一次抉择都留下回响。</p></div></div>
     <div class="home-step"><span>03</span><div><b>留下你的生涯</b><p>追逐荣誉，记录起伏，在终章回望自己的篮球故事。</p></div></div>
    </section>
   </div>
   <p class="home-footer">自动保存进度 · 支持导入与导出存档 · 按自己的节奏，打完这一生</p>
  </main>`;
}
''', '首页入口与存档管理')

# 保留实际 DOM 节点，确保返回后通过 onclick 绑定的事件选项仍可点击。
section('let STAGE_STACK=[];', 'function saveNow(){', r'''let STAGE_STACK=[];
function openOvl(html,width){
  if(window.matchMedia&&window.matchMedia('(min-width:900px)').matches){
    const st=document.querySelector('#stage');
    if(st){
      STAGE_STACK.push({nodes:Array.from(st.childNodes),fid:FUNC_CUR||null,scrollY:window.scrollY});
      st.innerHTML='<div class="funcnav"><button class="func-return" onclick="returnToEvent()">← 返回事件</button>'
        +(STAGE_STACK.length>1?'<button onclick="closeOvl()">返回上一级</button>':'')
        +'</div><div class="funcpage">'+html+'</div>';
      window.scrollTo(0,0);
      return;
    }
  }
  const box=document.querySelector('#ovl .box');if(box){box.classList.remove('wide','mid');if(width==='wide')box.classList.add('wide');else if(width==='mid')box.classList.add('mid');}$('#ovlBody').innerHTML=html;$('#ovl').classList.add('on');$('#ovl').scrollTop=0;
}
function closeOvl(){
  const ovl=$('#ovl'),body=$('#ovlBody');
  if(ovl&&ovl.classList.contains('on')){
    ovl.classList.remove('on');if(body)body.innerHTML='';
    if(!STAGE_STACK.length){FUNC_CUR=null;markFunc(null);}
    return;
  }
  if(STAGE_STACK.length){
    const st=document.querySelector('#stage'),it=STAGE_STACK.pop();
    if(st)st.replaceChildren(...it.nodes);
    FUNC_CUR=it.fid||null;markFunc(FUNC_CUR);
    window.scrollTo(0,it.scrollY||0);
    return;
  }
  FUNC_CUR=null;markFunc(null);
}
function returnToEvent(){
  const ovl=$('#ovl');if(ovl&&ovl.classList.contains('on'))closeOvl();
  if(STAGE_STACK.length){STAGE_STACK.splice(1);closeOvl();}
  else{FUNC_CUR=null;markFunc(null);}
}
''', '功能页直接返回与事件节点保留')

section('function funcbarHTML(){', 'const FUNC_PAGE=', r'''function funcbarHTML(){
  const b=(f,t,cls='')=>{const on=f===(FUNC_CUR||'event');return `<button data-f="${f}" class="${cls}${on?' on':''}"${on?' aria-current="page"':''} onclick="openFunc('${f}')">${t}</button>`;};
  return b('event','▶ 当前事件')+'<div class="fbhead">球队与赛事</div>'
    +b('roster','👥 阵容')
    +((S.league==='CBA'||S.league==='NBA'||S.league==='欧洲')?b('standings','📊 排名'):'')
    +(isPro()?b('picks','📋 签位'):'')+(S.bracket?b('bracket','🏆 对阵图'):'')
    +'<div class="fbhead">球员成长</div>'
    +b('attrs','📊 属性')+b('tend','🧭 倾向')+b('codex','🏅 成就')+b('archive','📋 档案')+b('money','💼 财务')
    +'<div class="fbhead">生涯管理</div>'
    +b('save','💾 存档')+b('export','📤 导出')+b('import','📥 导入')
    +b('sfx','🔊 '+(sfxEnabled()?'音效开':'音效关'))+b('end','🏁 结束生涯','dim');
}
''', '桌面功能分组')

sub1("document.querySelectorAll('.funcbar button[data-f]').forEach(b=>b.classList.toggle('on',b.getAttribute('data-f')===fid));",
     "document.querySelectorAll('.funcbar button[data-f]').forEach(b=>{const on=b.getAttribute('data-f')===(fid||'event');b.classList.toggle('on',on);if(on)b.setAttribute('aria-current','page');else b.removeAttribute('aria-current');});",
     '功能导航选中语义')

section('function openFunc(fid){', 'function renderFuncbar(){', r'''function openFunc(fid){
  if(fid==='event'){returnToEvent();return;}
  const page=FUNC_PAGE[fid];
  if(page){
    const same=FUNC_CUR===fid;
    if(STAGE_STACK.length){returnToEvent();if(same)return;}
    new Function(page)();
    FUNC_CUR=fid;markFunc(fid);
  }else{
    FUNC_ACT[fid]&&new Function(FUNC_ACT[fid])();
    if(fid==='sfx')renderFuncbar();
  }
}
''', '同级功能切换与再次点击返回事件')
sub1("return !!(o&&o.classList.contains('on'));",
     "return !!(o&&o.classList.contains('on'))||STAGE_STACK.length>0;", '功能页支持 Escape 返回')

sub1('if(fb)fb.innerHTML=funcbarHTML();', 'if(fb){fb.innerHTML=funcbarHTML();markFunc(FUNC_CUR);}', '侧栏重绘保留当前页')

sub1('<div id="chs"></div>', '<div class="decision-head"><h2 id="choiceTitle">做出你的选择</h2><span>${ev.choices.length} 个选项</span></div><div id="chs" aria-labelledby="choiceTitle"></div>', '事件决策标题')

sub1('<div class="result"><p class="out">${paras(ch0.o||\'\')}</p>',
     '<div class="result"><div class="result-choice"><span>你的选择</span><b>${esc(ch0.t)}</b></div><div class="out">${paras(ch0.o||\'\')}</div>',
     '结果页选择回顾与段落结构')
sub1('<div class="panel"><b>【状态面板】</b><br>',
     '<details class="result-status"><summary>查看球员完整状态</summary><div class="panel">', '结果状态按需展开')
sub1('${skillLine()}</div></div>', '${skillLine()}</div></details></div>', '结果状态折叠容器闭合')

# 原生控件优先处理自己的按键，避免展开状态/点击工具按钮时误触剧情继续。
sub1('if(typing(e.target))return;', 'if(e.defaultPrevented||typing(e.target))return;', '尊重已处理的键盘事件')
sub1('    const k=e.key,list=optList();',
     "    if(e.target.closest&&e.target.closest('summary,a[href],button:not(.ch),[role=\"button\"]'))return;\n    const k=e.key,list=optList();",
     '原生控件键盘优先')

# 模式卡补足键盘入口；弹层关闭按钮补无障碍名称。
for mode in ('immersive', 'fast'):
    old = 'onclick="startWithMode(\'%s\')"' % mode
    new = old + ' role="button" tabindex="0" onkeydown="if(event.key===\'Enter\'||event.key===\' \'){event.preventDefault();this.click();}"'
    sub1(old, new, '模式卡键盘操作 ' + mode)
sub1('<button class="x" onclick="closeOvl()">', '<button class="x" aria-label="关闭面板" onclick="closeOvl()">', '弹层关闭名称')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('界面层级与响应式精修已应用：%d -> %d 字符（%+d）' % (orig, len(s), len(s) - orig))
