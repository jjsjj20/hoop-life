# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 49：功能页适配新界面（v5.0.2）

【背景】用户需求「功能适配新界面」——v5.0.1 功能页虽已覆盖事件区，但还差两块：
  1. 功能竖栏没有「当前页面」指示——点了阵容，竖栏看不出自己在哪一层；
  2. 音效开关的文案（开/关）切换后竖栏不刷新。

【改动】
  1. 功能竖栏按钮改 openFunc(fid) 分发（data-f 标记），页面类（阵容/排名/签位/
     对阵图/财务/成就/档案/属性/倾向/导入）打开时 markFunc 高亮对应按钮；
     动作类（音效/导出/存档/结束）直接执行，执行后重渲竖栏（音效文案刷新）。
  2. STAGE_STACK 改对象栈 {html,fid}——逐层返回时恢复上一层的高亮。
  3. CSS：.funcbar button.on 高亮（金边金字）。
  手机端 overlay 弹窗逻辑不变（markFunc 在无 funcbar 时安全跳过）。
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


# ═══════════ 1. STAGE_STACK 对象化（栈项带 fid） ═══════════
sub1("    if(st){STAGE_STACK.push(st.innerHTML);",
     "    if(st){STAGE_STACK.push({html:st.innerHTML,fid:FUNC_CUR||null});", 'push 对象')
sub1("""    if(st)st.innerHTML=STAGE_STACK.pop();
    return;""",
"""    const it=STAGE_STACK.pop();
    if(st)st.innerHTML=it.html;
    FUNC_CUR=it.fid||null;markFunc(FUNC_CUR);
    return;""", 'pop 恢复+高亮')

# ═══════════ 2. renderGame 清栈时重置高亮 ═══════════
sub1("""    STAGE_STACK=[];   /* v5.0.1：界面重渲=功能页栈作废 */""",
"""    STAGE_STACK=[];   /* v5.0.1：界面重渲=功能页栈作废 */
    FUNC_CUR=null;""", 'renderGame 重置')

# ═══════════ 3. funcbarHTML：data-f + openFunc 分发 + 音效动态文案 ═══════════
sub1("""function funcbarHTML(){
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
}""",
"""function funcbarHTML(){
  /* v5.0.2：按钮改 data-f + openFunc 分发——页面类打开时高亮对应按钮（当前页面指示） */
  const b=(f,t,cls)=>'<button data-f="'+f+'"'+(cls?' class="'+cls+'"':'')+' onclick="openFunc(\\''+f+'\\')">'+t+'</button>';
  let h=b('roster','👥 阵容')
    +((S.league==='CBA'||S.league==='NBA'||S.league==='欧洲')?b('standings','📊 排名'):'')
    +(isPro()?b('picks','📋 签位'):'')
    +(S.bracket?b('bracket','🏆 对阵图'):'')
    +b('money','💼 财务')+b('codex','🏅 成就')+b('archive','📋 档案')
    +b('attrs','📊 属性','hot')+b('tend','🧭 倾向')
    +b('sfx','🔊 '+(sfxEnabled()?'音效开':'音效关'))
    +b('export','📤 导出')+b('import','📥 导入')+b('save','💾 存档')
    +b('end','🏁 结束生涯','dim');
  return '<div class="fbhead">功能</div>'+h;
}
const FUNC_PAGE={roster:'showRoster()',standings:'showStandings()',picks:'showPickAssets()',bracket:'showBracket()',money:'showMoney()',codex:'showCodex()',archive:'showArchive()',attrs:'showAttrs()',tend:'showTendHelp()',import:'openImport()'};
const FUNC_ACT={sfx:'toggleSfx()',export:'exportSave()',save:'saveNow()',end:'endNow()'};
let FUNC_CUR=null;   /* v5.0.2：当前功能页 id（funcbar 高亮指示） */
function markFunc(fid){
  document.querySelectorAll('.funcbar button[data-f]').forEach(b=>b.classList.toggle('on',b.getAttribute('data-f')===fid));
}
function openFunc(fid){
  const page=FUNC_PAGE[fid];
  if(page){new Function(page)();   /* 页面函数内部先 push 被覆盖层（此时 FUNC_CUR=旧层） */
    FUNC_CUR=fid;markFunc(fid);}
  else{FUNC_ACT[fid]&&new Function(FUNC_ACT[fid])();
    if(fid==='sfx')renderFuncbar();}   /* 音效开关文案刷新 */
}
function renderFuncbar(){const fb=document.querySelector('.funcbar');if(fb)fb.innerHTML=funcbarHTML();}""", 'funcbar 分发')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('功能页 2K 界面适配已应用：%d -> %d 字符（%+d）' % (orig, len(s), len(s) - orig))
