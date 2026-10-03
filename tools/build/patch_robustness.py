# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 5：把评审里的第 5、6 条做掉。

第 5 条 · 未捕获异常不再被静默吞掉
    原实现 `window.addEventListener('error',()=>recover())` 只求"别白屏"，
    错误的 message / 位置 / 堆栈一概丢弃，真实 bug 永远暴露不出来——
    玩家遇到的是"剧情突然跳到别处"，开发者这边什么都没有。
    现在：控制台留完整日志 + 内存留最近 20 条（档案面板可见，手机上也能自查）
        + 补上 unhandledrejection（AI 点评全是 Promise，被拒时会静默消失）
        + 同一条错误去重计数、玩家侧提示限流。

第 6 条 · AI 密钥明文存 localStorage 的知情与退出
    不加密（没有口令的加密只是障眼法），做两件真正有用的事：
    把"共用电脑上别填"写在密钥输入框正下方，并给一个一键清除密钥的出口。
"""
import os

BASE = os.path.dirname(os.path.abspath(__file__))
HTML = os.environ.get('GAME_HTML') or os.path.join(BASE, '..', 'output', '篮球人生.html')

s = open(HTML, encoding='utf-8').read()
orig = len(s)


def sub1(old, new, why):
    n = s.count(old)
    if n != 1:
        raise SystemExit('!! %s 匹配 %d 次' % (why, n))
    return s.replace(old, new)


# ═══════════ 第 5 条：崩溃恢复不再静默 ═══════════
OLD_RECOVER = """let recovering=false;
function recover(){
  if(recovering||!S)return;
  recovering=true;
  try{UI={mode:'event',ev:safeEvent()};save();renderGame();}catch(e){}
  recovering=false;
}
window.addEventListener('error',()=>recover());"""

NEW_RECOVER = """let recovering=false;
/* 崩溃自恢复：兜住未捕获异常，把玩家拉回一个安全事件页，而不是白屏。
 * 但「不白屏」不等于「当没发生」——早先这里完全静默，真实 bug 永远暴露不出来：
 * 玩家看到的是"剧情突然跳到别处"，开发者这边什么都没有。现在：
 *   · 控制台打一条带位置和堆栈的 [崩溃] 日志（本地调试 / 远程排查都能查）
 *   · 内存里留最近 20 条（不进存档、不撑大 localStorage），档案面板可见——
 *     手机上没有控制台，玩家也能截图反馈
 *   · 同一条错误反复出现只累加次数、不刷屏；玩家侧提示 30 秒最多一次
 */
const CRASH_LOG=[];
const CRASH_MAX=20;
let _crashToastAt=0;
function crashNote(src,msg,detail){
  const now=Date.now();
  const rec={t:now,src:String(src||'异常'),msg:String(msg==null?'未知错误':msg).slice(0,300),detail:detail?String(detail).slice(0,800):''};
  const last=CRASH_LOG[CRASH_LOG.length-1];
  if(last&&last.src===rec.src&&last.msg===rec.msg){last.n=(last.n||1)+1;last.t=now;}
  else{CRASH_LOG.push(rec);if(CRASH_LOG.length>CRASH_MAX)CRASH_LOG.shift();}
  try{console.error('[崩溃] '+rec.src+' · '+rec.msg+(rec.detail?('\\n'+rec.detail):''));}catch(_){}
  if(now-_crashToastAt>30000){
    _crashToastAt=now;
    try{toast('⚠️ 刚遇到一点异常，已自动回到安全进度（详情见「档案 → 运行日志」）');}catch(_){}
  }
}
function recover(){
  if(recovering||!S)return;
  recovering=true;
  try{UI={mode:'event',ev:safeEvent()};save();renderGame();}
  catch(e){crashNote('恢复流程自身出错',(e&&e.message)||e,(e&&e.stack)||'');}
  recovering=false;
}
window.addEventListener('error',function(e){
  /* 图片、脚本等资源加载失败也会冒泡到 window，它们没有 message，
   * 不该被当成代码崩溃记一笔（否则网络抖动就刷满日志）。 */
  if(e&&e.target&&e.target!==window&&e.target.tagName)return;
  const at=((e&&e.filename)||'')+((e&&e.lineno)?(':'+e.lineno+':'+((e&&e.colno)||0)):'');
  crashNote('脚本异常',(e&&e.message)||e,(at+(e&&e.error&&e.error.stack?('\\n'+e.error.stack):'')));
  recover();
});
window.addEventListener('unhandledrejection',function(e){
  /* AI 点评 / 实时事件流全程是 Promise，被拒绝时会静默消失，这里必须收住 */
  const r=e&&e.reason;
  crashNote('未处理的 Promise',(r&&r.message)||r,(r&&r.stack)||'');
});"""

s = sub1(OLD_RECOVER, NEW_RECOVER, '替换 recover / error 监听')

# 档案面板里加一节「运行日志」
ARCHIVE_TAIL = """     <button class="btn ghost" onclick="toggleSfx();showArchive()">${sfxEnabled()?'🔇 关掉音效':'🔊 打开音效'}</button>
   </div></div>`;
  openOvl(h);
}"""
ARCHIVE_NEW = """     <button class="btn ghost" onclick="toggleSfx();showArchive()">${sfxEnabled()?'🔇 关掉音效':'🔊 打开音效'}</button>
   </div></div>`;
  if(CRASH_LOG.length){
    h+=`<label>🧾 运行日志</label><div class="mini">本次运行捕获到 <b style="color:#ffd479">${CRASH_LOG.length}</b> 条异常（已自动恢复到安全进度，不影响存档）。遇到问题时把这一节截图反馈即可：</div>
     <div style="margin-top:6px">${CRASH_LOG.slice().reverse().map(r=>`<div class="tl"><span>${new Date(r.t).toLocaleTimeString()}</span><b>${esc(r.src)}：${esc(r.msg)}${(r.n||1)>1?(' ×'+r.n):''}</b></div>`).join('')}</div>`;
  }
  openOvl(h);
}"""
s = sub1(ARCHIVE_TAIL, ARCHIVE_NEW, '档案面板加运行日志')

# ═══════════ 第 6 条：密钥知情 + 一键清除 ═══════════
OLD_KEY = """ +'<label class="aiL">API Key</label><input id="aiKey" class="aiIn" type="password" value="'+esc(c.key||'')+'" placeholder="sk-...（仅存本机）">'"""
NEW_KEY = """ +'<label class="aiL">API Key</label><input id="aiKey" class="aiIn" type="password" value="'+esc(c.key||'')+'" placeholder="sk-...（仅存本机）">'
 +'<p class="mini" style="color:#ffd479;margin:6px 0 0">⚠️ 密钥以<b>明文</b>存在这台设备的浏览器里（不进存档、不进仓库，换设备需重填）。<b>共用 / 公共电脑上请不要填写</b>；不再使用就点下面的「🗑 清除密钥」。</p>'"""
s = sub1(OLD_KEY, NEW_KEY, '密钥输入框下方加提示')

OLD_ROW = """ +'<div class="aiRow"><button class="btn" onclick="AI.saveFromPanel()">💾 保存</button><button class="btn" onclick="AI.test()">🔌 测试连接</button><button class="btn" onclick="AI.clearCache()">🧹 清空缓存</button></div>'"""
NEW_ROW = """ +'<div class="aiRow"><button class="btn" onclick="AI.saveFromPanel()">💾 保存</button><button class="btn" onclick="AI.test()">🔌 测试连接</button><button class="btn" onclick="AI.clearCache()">🧹 清空缓存</button><button class="btn ghost" onclick="AI.clearKey()">🗑 清除密钥</button></div>'"""
s = sub1(OLD_ROW, NEW_ROW, 'AI 面板加清除密钥按钮')

OLD_CC = """AI.clearCache=function(){try{localStorage.removeItem('hoop_ai_cache_v1');if(typeof toast==='function')toast('已清空 AI 缓存 🧹');}catch(e){}};"""
NEW_CC = OLD_CC + """
/* 清除本机保存的密钥：不加密（没有口令的加密只是障眼法），
 * 真正有用的是「说清楚它存在哪」+「随时能一键抹掉」。 */
AI.clearKey=function(){
 if(!confirm('清除这台设备上保存的 API 密钥，并关闭 AI 点评？\\n（只影响本机设置，存档不受影响）'))return;
 AI.cfg.key='';
 AI.cfg.on=false;
 AI.saveCfg();
 const k=document.getElementById('aiKey');if(k)k.value='';
 const on=document.getElementById('aiOn');if(on)on.checked=false;
 const o=document.getElementById('aiTestOut');if(o)o.textContent='🔒 已清除密钥，AI 点评已关闭';
 if(typeof toast==='function')toast('已清除本机保存的 API 密钥 🔒');
};"""
s = sub1(OLD_CC, NEW_CC, '新增 AI.clearKey')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('第 5、6 条已应用：%d -> %d 字符（+%d）' % (orig, len(s), len(s) - orig))
