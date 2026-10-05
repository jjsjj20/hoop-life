# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 27：AI 只输出正文（v4.20.3）

反馈：模型会把「草稿：…」「检查：…」「（约160字）」这类自我说明和字数括注
一起交出来——需要它只给正文。

两处改（一处统一加规则、一处兜底清洗，不做逐条提示词改动）：
  ① AI.ask 在系统提示词末尾统一追加【输出格式】规则——
     文本类：「只输出正文本身：直接给成文内容；不要前言、草稿、自检、字数统计、
             括注、说明或 Markdown 标记；不要复述要求，不要用引号把全文包起来。」
     JSON 类：「只输出一个 JSON 对象本身：不要前言、说明、代码块或任何多余文字。」
  ② AI.san 兜底清洗：去代码围栏、去字数括注、去开头寒暄/说明行（草稿|检查|注|字数…）、
     去整体包裹的引号、去行首标签——即使模型不守规矩，展示出来的也只是正文。
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


# ═══════════ ① 输出格式规则（AI.ask 统一追加）═══════════
sub1("""AI.ask=function(sys,user,opt){
 const mt0=(opt&&opt.mt)||900;""",
"""/* v4.20.3：所有生成统一「只输出正文」——一处加规则，覆盖战报/颁奖/里程碑/终章/报纸/事件 */
AI.RULE_ONLY='【输出格式】只输出正文本身：直接给成文内容；不要前言、草稿、自检、字数统计、括注、说明或 Markdown 标记；不要复述要求，不要用引号把全文包起来。';
AI.RULE_JSON='【输出格式】只输出一个 JSON 对象本身：不要前言、说明、代码块或任何多余文字。';
AI.ask=function(sys,user,opt){
 const mt0=(opt&&opt.mt)||900;""", '输出格式规则常量')

sub1("""     messages:[{role:'system',content:sys},{role:'user',content:user}],""",
"""     messages:[{role:'system',content:String(sys||'')+(useJson?AI.RULE_JSON:AI.RULE_ONLY)},{role:'user',content:user}],""", '系统提示词追加规则')

# ═══════════ ② AI.san 兜底清洗 ═══════════
sub1("""AI.san=function(t,max){t=String(t||'').replace(/[<>]/g,'').split(String.fromCharCode(13)).join('');const d=AI_NL+AI_NL,d3=d+AI_NL;while(t.indexOf(d3)>=0)t=t.split(d3).join(d);return t.trim().slice(0,Math.max(200,Number(max)||700));};   /* v4.20.2：报纸等长文可传自定义上限 */""",
"""/* v4.20.3：清洗兜底——即使模型不守「只输出正文」，展示出来的也只是正文 */
AI.san=function(t,max){
 t=String(t||'').replace(/[<>]/g,'').split(String.fromCharCode(13)).join('');
 t=t.split('```').join('');                                   /* 代码围栏 */
 t=t.replace(/[（(](?:约|共|全文|字数)? ?[0-9]{1,4} ?字[)）]/g,'');
 const lines=(AI_NL+t).split(AI_NL).map(function(x){return x.trim();});
 const meta=/^(?:好的|当然|没问题|没问题[，,]|以下是|这是|下面是|为你|草稿|正文|说明|注[：:]|备注|检查|自检|字数|要求|提示|——)/;
 let i=0;
 while(i<lines.length&&(lines[i]===''||(meta.test(lines[i])&&lines[i].indexOf('。')<0&&lines[i].length<40)))i++;   /* 只吃开头的寒暄/说明行 */
 lines.splice(0,i);
 let out=lines.join(AI_NL).trim();
 out=out.replace(/^[“"「『]([^]*)[”"」』]$/,function(m,a){return a;});
 out=out.replace(/^(?:草稿|正文|说明|注|备注|检查|字数|要求)[：:] */g,'');
 const d=AI_NL+AI_NL,d3=d+AI_NL;while(out.indexOf(d3)>=0)out=out.split(d3).join(d);
 return out.trim().slice(0,Math.max(200,Number(max)||700));
};""", 'san 兜底清洗')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('只输出正文已应用：%d -> %d 字符（%+d）' % (orig, len(s), len(s) - orig))
