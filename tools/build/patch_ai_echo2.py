# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 29：回声检测收紧 + 报纸重试（v4.20.5）

反馈：「体育报说模型在复述要求」——v4.20.4 的回声检测误报了。
原因：判定过宽——事实标签（球员：/结果：…）只要命中 2 个就判回声，
而报纸正文天然会引用这些标签；"要求：/字数/Markdown" 也是弱特征，
正常文本可能出现。

修复：
  ① 改为打分制：
     · 强特征（只在提示词里出现）命中 1 个即判回声：不能编造 / 只使用给定 / 【任务】 / 【事实】 / 不要复述
     · 弱特征需 ≥2 个：要求：/ 字数 / Markdown
     · 事实标签需 ≥3 个（回声通常带 5~6 个，正常文章引 1~2 个不再误伤）
  ② 报纸（AI.newsGo）与战报同样待遇：判为回声 → 带加强指令重试一次；仍回声才报错且不写缓存。
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


# ═══════════ ① 回声判定改打分制 ═══════════
sub1("""AI.looksLikeEcho=function(t){
 const x=String(t||'');
 if(/要求[:：]|不能编造|只使用给定|Markdown|字数\\s*[:：]|【任务】|【事实】/.test(x))return true;
 const labels=['球员：','比赛：','结果：','个人数据：','系统旁白：','分节得分：','关键时刻：'];
 let hit=0;labels.forEach(function(k){if(x.indexOf(k)>=0)hit++;});
 return hit>=2;
};""",
"""AI.looksLikeEcho=function(t){
 /* v4.20.5：改打分制——避免误伤（报纸正文天然会引用「结果：」这类标签） */
 const x=String(t||'');
 if(/不能编造|只使用给定|【任务】|【事实】|不要复述/.test(x))return true;   /* 强特征：只在提示词里出现 */
 let weak=0;
 ['要求：','要求:','字数','Markdown'].forEach(function(k){if(x.indexOf(k)>=0)weak++;});
 if(weak>=2)return true;                                                  /* 弱特征需≥2 */
 const labels=['球员：','比赛：','结果：','个人数据：','系统旁白：','分节得分：','关键时刻：'];
 let hit=0;labels.forEach(function(k){if(x.indexOf(k)>=0)hit++;});
 return hit>=3;                                                           /* 事实标签需≥3（回声通常 5~6 个） */
};""", '回声判定打分制')

# ═══════════ ② 报纸：回声则重试一次 ═══════════
sub1(""" AI.ask(b.sys,b.user,{mt:900}).then(function(t){
  const txt=AI.san(t,1200);   /* v4.20.2：多段长文（报纸）不再被 700 字截断 */
  if(!txt)throw new Error('返回内容为空');
  /* v4.20.4：回声检测——复述要求/素材的报纸不入缓存 */
  if(AI.looksLikeEcho(txt))throw new Error('模型在复述要求，请重试或换一个模型');
  AI.busy=false;
  AI.cSet(b.key,txt);""",
""" AI.ask(b.sys,b.user,{mt:900}).then(function(t){
  const txt=AI.san(t,1200);   /* v4.20.2：多段长文（报纸）不再被 700 字截断 */
  if(!txt)throw new Error('返回内容为空');
  /* v4.20.5：回声 → 重试一次（带加强指令）；仍回声才报错，且不写缓存 */
  if(AI.looksLikeEcho(txt)){
   return AI.ask(b.sys,b.user+'\\n【再次强调】只写报纸正文，不要复述上面的要求或素材。',{mt:900}).then(function(t2){
    const txt2=AI.san(t2,1200);
    if(!txt2||AI.looksLikeEcho(txt2))throw new Error('模型在复述要求，请重试或换一个模型');
    AI.busy=false;
    AI.cSet(b.key,txt2);
    const wrap2=document.getElementById('npWrap');
    if(wrap2)wrap2.innerHTML=AI.newsMast()+AI.newsHTML(txt2,b.key);
    try{sfx('msg');}catch(e){}
    if(typeof toast==='function')toast('本期报纸已出刊 📰');
   });
  }
  AI.busy=false;
  AI.cSet(b.key,txt);""", '报纸回声重试')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('回声检测收紧已应用：%d -> %d 字符（%+d）' % (orig, len(s), len(s) - orig))
