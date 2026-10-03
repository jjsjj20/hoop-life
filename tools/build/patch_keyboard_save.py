# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 2 + 3
2) 全局键盘操作：数字选选项 / ↑↓ 移动高亮 / Enter·空格确认 / Esc 关弹窗
3) 存档导出与导入：下载 json、粘贴或选文件导入，写入前自动备份
在 output/篮球人生.html 上原地打补丁。
"""
import os, re, sys

BASE = os.path.dirname(os.path.abspath(__file__))
HTML = os.environ.get('GAME_HTML') or os.path.join(BASE, '..', 'output', '篮球人生.html')

s = open(HTML, encoding='utf-8').read()
orig = len(s)


def sub1(old, new, why):
    """要求唯一匹配，否则报错——避免在 2MB 文件里改错地方。"""
    n = s.count(old)
    if n != 1:
        print('!! 匹配 %d 次: %s' % (n, why))
        raise SystemExit(1)
    return s.replace(old, new)


# ═══════════ A. 样式 ═══════════
CSS = """
/* ── 键盘操作：↑↓ 高亮到的选项，要和 :hover 一样看得见焦点在哪 ───────── */
.ch.kbsel{border-color:var(--accent);background:var(--btn-hot);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.05),0 18px 34px -24px rgba(0,0,0,1),0 0 0 1px rgba(249,115,22,.34),0 14px 40px -24px rgba(249,115,22,.45)}
.ch.kbsel .idx{background:var(--accent);color:#fff}
.ch.kbsel .ctext{transform:translateX(2px)}
/* 键盘提示只给「有鼠标+精确指针」的桌面端看，触屏上不占地方 */
.kbhint{display:none}
@media(hover:hover) and (pointer:fine){.kbhint{display:block}}
/* ── 存档导出 / 导入 ────────────────────────────────────────────────── */
.svTa{width:100%;box-sizing:border-box;height:118px;resize:vertical;background:var(--field);color:var(--txt2);
  border:1px solid var(--line2);border-radius:10px;padding:10px 12px;font-size:12px;line-height:1.5;
  font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,"Courier New",monospace}
.svTa:focus{outline:none;border-color:var(--accent)}
.svPick{display:block;cursor:pointer;text-align:center;padding:14px;border:1px dashed var(--line2);
  border-radius:12px;background:var(--btn2);color:var(--txt4);font-size:13px;margin:10px 0;transition:border-color .16s,color .16s}
.svPick:hover{border-color:var(--accent);color:var(--accent-txt)}
.svRow{display:flex;gap:8px;margin-top:10px;flex-wrap:wrap}
.svRow button{flex:1;min-width:118px}
"""
# 追加到最后一个 <style>（v3.5 视觉精修层）之前，保证优先级压过前面的基础样式
_pos = s.rindex('</style>')
s = s[:_pos] + CSS.lstrip('\n') + s[_pos:]

# ═══════════ B. 事件页的键盘提示 ═══════════
s = sub1(
    """const f=document.createElement('div');f.className='mini';f.innerHTML='⚡ 可点「⏩ 快进」随机处理本事件';""",
    """const f=document.createElement('div');f.className='mini';
  f.innerHTML='⚡ 可点「⏩ 快进」随机处理本事件'
    +'<span class="kbhint"> ｜ ⌨️ 数字键 1-9 直接选，↑↓ 移动、Enter 确认</span>';""",
    'showEvent 提示')

# ═══════════ C. renderGame / renderResult 末尾补一行「空格继续」提示 ═══════════
# renderGame 之外还有直接落到结果页的路径（choose() → renderResult），两边都补上
s = sub1(
    """    window.scrollTo(0,0);
  }catch(e){recover();}
}""",
    """    kbHint();
    window.scrollTo(0,0);
  }catch(e){recover();}
}""",
    'renderGame 调用 kbHint')

s = sub1(
    """  <button class="btn" onclick="advance()">继续 ▶</button>`;
}""",
    """  <button class="btn" onclick="advance()">继续 ▶</button>`;
  kbHint();
}""",
    'renderResult 调用 kbHint')

# ═══════════ D. 存档导出 / 导入 ═══════════
SAVE_CODE = r"""
/* ---- 存档导出 / 导入 ----
 * localStorage 是单点：玩家清一次浏览器数据，主存档和 .autobak 备份会一起没。
 * 这里给一条玩家自己能掌控的退路——导出成 JSON 文件（或一段文本）随身带走，
 * 换电脑 / 换浏览器 / 换域名之后粘回来，接着打。
 */
function saveStamp(){
  const d=new Date(),p=n=>String(n).padStart(2,'0');
  return d.getFullYear()+p(d.getMonth()+1)+p(d.getDate())+'-'+p(d.getHours())+p(d.getMinutes());
}
function exportSave(){
  /* 主菜单里 S 是空的，但存档还在 localStorage —— 那种情况直接导出存着的那份 */
  let j='';
  if(S){j=saveJson();}
  else{try{j=localStorage.getItem(CFG.SAVE_KEY)||'';}catch(e){j='';}}
  if(!j){toast(S?'⚠️ 导出失败：存档序列化出错':'还没有存档可以导出，先开始一局吧');return;}
  let nm='';
  try{nm=((JSON.parse(j)||{}).S||{}).name||'';}catch(e){}
  const name='hooplife-存档-'+saveStamp()+(nm?'-'+String(nm).replace(/[\\/:*?"<>|\s]+/g,''):'')+'.json';
  try{
    const url=URL.createObjectURL(new Blob([j],{type:'application/json'}));
    const a=document.createElement('a');
    a.href=url;a.download=name;document.body.appendChild(a);a.click();
    setTimeout(()=>{try{URL.revokeObjectURL(url);a.remove();}catch(_){}},1500);
    toast('📤 已导出 '+name+'（'+(j.length/1024).toFixed(0)+' KB）');
  }catch(e){
    /* 少数环境禁用了 a[download]：退回到「复制文本」，别让这条路直接断掉 */
    showSaveText(j,'📤 存档文本（手动复制保存）',
      '你的浏览器拦下了自动下载。把下面整段复制走，存成 .json 文件；下次用「📥 导入存档」粘回来即可。');
  }
}
function showSaveText(j,title,note){
  openOvl(`<h3>${title}</h3>
   <div class="mini">${note}</div>
   <textarea class="svTa" id="saveTa" spellcheck="false"></textarea>
   <div class="svRow"><button class="btn" onclick="pickSaveTa()">📋 全选这段文本</button>
   <button class="btn ghost" onclick="closeOvl()">关闭</button></div>`,'mid');
  const ta=$('#saveTa');if(ta){ta.value=j;ta.focus();ta.select();}
}
function pickSaveTa(){const ta=$('#saveTa');if(ta){ta.focus();ta.select();toast('已全选，按 Ctrl+C 复制');}}
function openImport(){
  openOvl(`<h3>📥 导入存档</h3>
   <div class="mini">选一个之前导出的 .json 存档，或者把存档文本直接粘进下面的框里。</div>
   <label class="svPick">📁 选择存档文件<input type="file" accept=".json,application/json" onchange="importSaveFile(event)" style="display:none"></label>
   <div class="mini" style="margin-top:4px">或者粘贴存档文本：</div>
   <textarea class="svTa" id="saveTaIn" spellcheck="false" placeholder='{"v":2,"S":{...}}'></textarea>
   <div class="svRow"><button class="btn" onclick="importSaveText()">✅ 导入并继续生涯</button>
   <button class="btn ghost" onclick="closeOvl()">取消</button></div>`,'mid');
}
function importSaveText(){
  const ta=$('#saveTaIn');
  applySaveText(ta?ta.value:'');
}
function importSaveFile(ev){
  const f=ev.target.files&&ev.target.files[0];if(!f)return;
  const r=new FileReader();
  r.onload=()=>{try{applySaveText(String(r.result||''));}catch(e){toast('读取文件失败');}};
  r.onerror=()=>toast('读取文件失败');
  r.readAsText(f,'utf-8');
  ev.target.value='';   /* 清空，方便连续选同一个文件 */
}
function applySaveText(txt){
  txt=String(txt||'').replace(/^\uFEFF/,'').trim();
  if(!txt){toast('粘贴框是空的');return;}
  let d=null;
  try{d=JSON.parse(txt);}catch(e){d=null;}
  if(!d||!d.S||typeof d.S!=='object'){toast('⚠️ 这段内容不是本游戏的存档');return;}
  /* 来自更新版本的存档先拦一下：字段含义可能已经变了，硬读会得到一局诡异的数据 */
  if(typeof d.v==='number'&&d.v>CFG.SAVE_VER){
    if(!confirm('这个存档来自更新的版本（v'+d.v+' > 当前 v'+CFG.SAVE_VER+'），读取后可能出现异常。仍然继续？'))return;
  }
  const nm=(d.S&&d.S.name)||'未知',age=(d.S&&d.S.age)||'?';
  if(!confirm('导入会覆盖当前存档：'+nm+' · '+age+'岁。\n确定继续吗？（旧存档会先自动备份，之后可用「恢复自动备份」找回）'))return;
  try{_autoBak();localStorage.setItem(CFG.SAVE_KEY,JSON.stringify({v:CFG.SAVE_VER,S:d.S,UI:d.UI||null}));}
  catch(e){toast('⚠️ 写入失败：浏览器存储空间可能已满');return;}
  S=null;UI=null;
  closeOvl();
  try{continueGame();}catch(e){renderMenu();}
  toast('📥 已导入存档：'+nm+' · '+age+'岁');
}
"""
s = sub1(
    """function saveNow(){toast(save()?'已存档 💾':'⚠️ 存档失败：浏览器存储空间不足');}
""",
    """function saveNow(){toast(save()?'已存档 💾':'⚠️ 存档失败：浏览器存储空间不足');}
""" + SAVE_CODE,
    '插入存档导出/导入函数')

# ═══════════ E. 主菜单入口 ═══════════
s = sub1(
    """    <button class="btn ghost" onclick="continueGame()">📂 读取存档，继续生涯</button>
    <button class="minibtn" onclick="delSave()">🗑 清除存档</button>""",
    """    <button class="btn ghost" onclick="continueGame()">📂 读取存档，继续生涯</button>
    <button class="minibtn" onclick="exportSave()">📤 导出存档（存成文件随身带走）</button>
    <button class="minibtn" onclick="openImport()">📥 导入存档（从文件或文本恢复）</button>
    <button class="minibtn" onclick="delSave()">🗑 清除存档</button>""",
    '主菜单 有存档 时的入口')

s = sub1(
    """`<div class="mini" style="margin:0">暂无存档 · 点击下方开始一段新的生涯</div>`)}""",
    """`<div class="mini" style="margin:0 0 2px">暂无存档 · 点击下方开始一段新的生涯</div>
     <button class="minibtn" onclick="openImport()">📥 已有存档文件？从这里导入</button>`)}""",
    '主菜单 无存档 时的导入入口')

# ═══════════ F. 游戏内顶栏入口 ═══════════
s = sub1(
    """     <button onclick="saveNow()">💾 存档</button>""",
    """     <button onclick="saveNow()">💾 存档</button>
     <button onclick="exportSave()">📤 导出</button>
     <button onclick="openImport()">📥 导入</button>""",
    '游戏顶栏入口')

# ═══════════ G. 键盘操作 ═══════════
KB_CODE = r"""
/* ═══════════ 11.5 键盘操作 ═══════════
 * 桌面玩家第一反应是敲键盘，不是找鼠标。这里把常用动作接到按键上：
 *   1-9          直接选择对应编号的剧情选项
 *   ↑ / ↓        在选项间移动高亮（高亮态与 :hover 同款，看得见）
 *   Enter / 空格  确认当前高亮的选项
 *   空格 / Enter  没有选项时触发「继续 ▶」这类主按钮（结算 / 赛季总结 / 下一年）
 *   Esc          关掉弹出的面板 / 取消当前高亮
 * 生效范围只有游戏主区 #stage：建档页、AI 设置面板这些有输入框的地方完全放行，
 * 弹窗打开时也不抢键，避免误触。
 */
function kbHint(){
  const st=document.getElementById('stage');
  if(!st||st.querySelector('.ch')||st.querySelector('.kbhint'))return;
  const bs=st.querySelectorAll('button.btn');
  let btn=null;
  for(let i=0;i<bs.length;i++){if(!bs[i].classList.contains('ghost')&&!bs[i].disabled){btn=bs[i];break;}}
  if(!btn)return;
  const d=document.createElement('div');
  d.className='kbhint mini';
  d.style.cssText='text-align:center;margin:10px 0 -6px';
  d.textContent='⌨️ 空格 / Enter 也可以继续';
  btn.parentNode.insertBefore(d,btn);
}
(function(){
  const SEL='kbsel';
  function typing(el){
    if(!el)return false;
    const t=(el.tagName||'').toUpperCase();
    return t==='INPUT'||t==='TEXTAREA'||t==='SELECT'||el.isContentEditable===true;
  }
  function ovlOpen(){const o=document.getElementById('ovl');return !!(o&&o.classList.contains('on'));}
  function stageEl(){return document.getElementById('stage');}
  function optList(){
    const st=stageEl();if(!st)return [];
    const box=st.querySelector('#chs');
    if(!box||box.dataset.locked)return [];
    return [].slice.call(box.querySelectorAll('.ch'));
  }
  function primaryBtn(){
    const st=stageEl();if(!st)return null;
    const bs=st.querySelectorAll('button.btn');
    for(let i=0;i<bs.length;i++){
      const b=bs[i];
      if(!b.classList.contains('ghost')&&!b.disabled)return b;
    }
    return null;
  }
  function hiOf(list){let k=-1;list.forEach((b,i)=>{if(b.classList.contains(SEL))k=i;});return k;}
  function paint(list,k){list.forEach((b,i)=>{b.classList.toggle(SEL,i===k);});}

  document.addEventListener('keydown',function(e){
    if(e.ctrlKey||e.metaKey||e.altKey)return;
    if(typing(e.target))return;

    if(ovlOpen()){
      if(e.key==='Escape'){e.preventDefault();try{closeOvl();}catch(_){}}
      return;
    }

    const k=e.key,list=optList();

    if(list.length){
      /* 数字键：直接选，不再要求先高亮 */
      if(k.length===1&&k>='1'&&k<='9'){
        const i0=k.charCodeAt(0)-49;
        if(i0<list.length){e.preventDefault();list[i0].click();}
        return;
      }
      if(k==='Escape'){paint(list,-1);return;}
      if(k==='ArrowDown'||k==='ArrowUp'){
        e.preventDefault();
        const cur=hiOf(list);
        const nx=k==='ArrowDown'?Math.min(list.length-1,cur+1):Math.max(0,cur<=0?0:cur-1);
        paint(list,nx);
        try{list[nx].scrollIntoView({block:'nearest'});}catch(_){}
        return;
      }
      if(k==='Enter'||k===' '||k==='Spacebar'){
        const cur=hiOf(list);
        /* 没有任何高亮就不动 —— 选项是要负责的，别让空格随手替玩家拍板 */
        if(cur<0)return;
        e.preventDefault();
        list[cur].click();
      }
      return;
    }

    if(k===' '||k==='Spacebar'||k==='Enter'){
      const b=primaryBtn();
      if(b){e.preventDefault();b.click();}
    }
  });
})();
"""
s = sub1(
    """window.addEventListener('error',()=>recover());
""",
    """window.addEventListener('error',()=>recover());
""" + KB_CODE,
    '插入键盘操作')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('ok: %d -> %d chars' % (orig, len(s)))
