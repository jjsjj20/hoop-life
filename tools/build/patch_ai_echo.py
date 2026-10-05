# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 28：AI 回声/复读检测与重试（v4.20.4）

反馈：「还是这样」——模型把任务要求与事实原样复述回来（甚至重复两遍后截断）。
这类输出一旦写入缓存，同一个事件会一直复现同样的垃圾。

修复：
  ① 规则加强：AI.RULE_ONLY 追加「不要复述题目、事实或要求」；
  ② AI.looksLikeEcho(t)：识别回声——命中指令词（要求：/不能编造/只使用给定/Markdown/
     字数/【任务】）或命中 ≥2 个事实标签（球员：/比赛：/结果：/个人数据：/系统旁白：/分节得分：）；
  ③ AI.go / AI.newsGo：清洗后先判回声 → 回声则带加强指令重试一次；
     仍为回声则报错并【不写缓存】（避免垃圾被缓存长期复现）；
  ④ 用户提示词加【任务】/【事实】分栏，明确「只写正文、不要复述」。
"""
import os

BASE = os.path.dirname(os.path.abspath(__file__))
HTML = os.environ.get('GAME_HTML') or os.path.join(BASE, '..', 'output', '篮球人生.html')

s = open(HTML, encoding='utf-8').read()
orig = len(s)


def sub1(old, new, why, cnt=1):
    global s
    n = s.count(old)
    if n != cnt:
        raise SystemExit('!! %s 匹配 %d 次（期望 %d）' % (why, n, cnt))
    s = s.replace(old, new)


# ═══════════ ① 规则加强 ═══════════
sub1("AI.RULE_ONLY='【输出格式】只输出正文本身：直接给成文内容；不要前言、草稿、自检、字数统计、括注、说明或 Markdown 标记；不要复述要求，不要用引号把全文包起来。';",
     "AI.RULE_ONLY='【输出格式】只输出正文本身：直接给成文内容；不要前言、草稿、自检、字数统计、括注、说明或 Markdown 标记；不要复述题目、事实或要求；不要用引号把全文包起来。';",
     '规则加强')

# ═══════════ ② 回声识别 ═══════════
sub1("""AI.ask=function(sys,user,opt){""",
"""/* v4.20.4：回声/复读识别——模型把要求或事实原样吐回来时，判定为无效输出 */
AI.looksLikeEcho=function(t){
 const x=String(t||'');
 if(/要求[:：]|不能编造|只使用给定|Markdown|字数\\s*[:：]|【任务】|【事实】/.test(x))return true;
 const labels=['球员：','比赛：','结果：','个人数据：','系统旁白：','分节得分：','关键时刻：'];
 let hit=0;labels.forEach(function(k){if(x.indexOf(k)>=0)hit++;});
 return hit>=2;
};
AI.ask=function(sys,user,opt){""", '回声识别')

# ═══════════ ③ AI.go：回声则重试一次，仍回声则报错且不写缓存 ═══════════
sub1(""" AI.ask(brief.sys,brief.user).then(function(t){
  AI.busy=false;
  const txt=AI.san(t);
  if(!txt)throw new Error('返回内容为空');
  AI.cSet(k2,txt);""",
""" AI.ask(brief.sys,brief.user).then(function(t){
  const txt=AI.san(t);
  if(!txt)throw new Error('返回内容为空');
  /* v4.20.4：回声（复述要求/事实）→ 带加强指令重试一次 */
  if(AI.looksLikeEcho(txt)){
   return AI.ask(brief.sys,brief.user+'\\n【再次强调】只写正文，不要复述上面的要求或事实。').then(function(t2){
    const txt2=AI.san(t2);
    if(!txt2||AI.looksLikeEcho(txt2))throw new Error('模型在复述要求，请重试或换一个模型');
    AI.busy=false;AI.cSet(k2,txt2);
    const box2=document.getElementById('aiBox');
    if(box2)box2.innerHTML=AI.boxHTML(kind,k2);
    try{sfx('msg');}catch(e){}
    if(typeof toast==='function')toast('AI 点评已生成 ✨');
   });
  }
  AI.busy=false;
  AI.cSet(k2,txt);""", 'AI.go 回声重试')

# ═══════════ ④ 报纸同样处理 ═══════════
sub1(""" AI.ask(b.sys,b.user,{mt:900}).then(function(t){
  AI.busy=false;
  const txt=AI.san(t,1200);   /* v4.20.2：多段长文（报纸）不再被 700 字截断 */
  if(!txt)throw new Error('返回内容为空');
  AI.cSet(b.key,txt);""",
""" AI.ask(b.sys,b.user,{mt:900}).then(function(t){
  const txt=AI.san(t,1200);   /* v4.20.2：多段长文（报纸）不再被 700 字截断 */
  if(!txt)throw new Error('返回内容为空');
  /* v4.20.4：回声检测——复述要求/素材的报纸不入缓存 */
  if(AI.looksLikeEcho(txt))throw new Error('模型在复述要求，请重试或换一个模型');
  AI.busy=false;
  AI.cSet(b.key,txt);""", '报纸回声检测')

# ═══════════ ⑤ 用户提示词分栏（战报）═══════════
sub1(""" const user='请根据以下比赛事实，写一段赛后战报：'+AI_NL+L.join(AI_NL);""",
""" const user='【任务】写一段赛后战报正文（只输出正文，不要复述本段事实或要求）。'+AI_NL+'【事实】'+AI_NL+L.join(AI_NL);""", '战报提示词分栏')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('回声检测与重试已应用：%d -> %d 字符（%+d）' % (orig, len(s), len(s) - orig))
