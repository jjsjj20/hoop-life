# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 48：功能页桌面下直接覆盖事件区（v5.0.1）

【背景】用户反馈：「点击功能后不要新的窗口直接覆盖事件」——桌面端点功能竖栏
  （阵容/排名/档案/属性等）会弹出 overlay 覆盖层，用户希望内容直接渲染在
  事件区内（覆盖当前事件），并可返回。

【实现】openOvl/closeOvl 分端：
  桌面（≥900px）：openOvl 把内容渲染进 #stage（原事件内容入栈）+ 底部「↩ 返回」；
    closeOvl 从栈弹出恢复上一层内容（支持 roster→otherTeams 等嵌套层级）；
    renderGame（新事件/界面重渲）清空栈。
  手机（<900px）：保持原 overlay 弹窗逻辑，完全不变。
  功能页样式复用全局 .summ/.card/.label/.bar 类，无新增依赖。
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


# ═══════════ 1. openOvl：桌面渲染进 #stage（栈式） ═══════════
sub1("""function openOvl(html,width){const box=document.querySelector('#ovl .box');if(box){box.classList.remove('wide','mid');if(width==='wide')box.classList.add('wide');else if(width==='mid')box.classList.add('mid');}$('#ovlBody').innerHTML=html;$('#ovl').classList.add('on');$('#ovl').scrollTop=0; /* 每次打开从顶部开始 */
}""",
"""let STAGE_STACK=[];   /* v5.0.1 桌面：功能页覆盖事件区——原内容入栈，可逐层返回 */
function openOvl(html,width){
  if(window.matchMedia&&window.matchMedia('(min-width:900px)').matches){
    const st=document.querySelector('#stage');
    if(st){STAGE_STACK.push(st.innerHTML);
      st.innerHTML='<div class="funcpage">'+html+'</div><button class="btn ghost" style="margin-top:14px" onclick="closeOvl()">↩ 返回</button>';
      window.scrollTo(0,0);
      return;}
  }
  const box=document.querySelector('#ovl .box');if(box){box.classList.remove('wide','mid');if(width==='wide')box.classList.add('wide');else if(width==='mid')box.classList.add('mid');}$('#ovlBody').innerHTML=html;$('#ovl').classList.add('on');$('#ovl').scrollTop=0; /* 每次打开从顶部开始 */
}""", 'openOvl 桌面分支')

# ═══════════ 2. closeOvl：桌面从栈恢复 ═══════════
sub1("""function closeOvl(){$('#ovl').classList.remove('on');const b=$('#ovlBody');if(b)b.innerHTML='';}""",
"""function closeOvl(){
  if(window.matchMedia&&window.matchMedia('(min-width:900px)').matches&&STAGE_STACK.length){
    const st=document.querySelector('#stage');
    if(st)st.innerHTML=STAGE_STACK.pop();
    return;
  }
  $('#ovl').classList.remove('on');const b=$('#ovlBody');if(b)b.innerHTML='';
}""", 'closeOvl 桌面分支')

# ═══════════ 3. renderGame 开头清栈（新界面=栈作废） ═══════════
sub1("""function renderGame(){
  try{
    if(!UI)UI={mode:'event',ev:null};""",
"""function renderGame(){
  try{
    if(!UI)UI={mode:'event',ev:null};
    STAGE_STACK=[];   /* v5.0.1：界面重渲=功能页栈作废 */""", 'renderGame 清栈')

# ═══════════ 4. funcpage 样式 ═══════════
sub1(".actions button:active{transform:scale(.97)}",
""".actions button:active{transform:scale(.97)}
/* ── v5.0.1 桌面功能页（直接覆盖事件区，非弹窗） ── */
.funcpage{padding:4px 0}
.funcpage .summ{margin-top:0}
.funcpage label{display:block;margin:14px 0 4px;color:var(--gold);font-size:12.5px;font-weight:700}""", 'funcpage 样式')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('功能页桌面覆盖已应用：%d -> %d 字符（%+d）' % (orig, len(s), len(s) - orig))
