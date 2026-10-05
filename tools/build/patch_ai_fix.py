# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 26：AI 生成兼容性修复（v4.20.2）

反馈：「AI 战报和其他生成不了，报『接口响应缺少内容』，但 AI 事件可以生成。」

定位：三类生成共用 AI.ask，差异在参数——
  · AI 事件：mt 800 + json（成功）
  · 战报/里程碑/赛季/报纸：默认 mt 360（失败）
思考型模型（reasoning，如 R1/o 系列/第三方推理模型）把 360 的预算吃在思考轨迹上，
留给正式内容的 token 所剩无几 → choices[0].message.content 为空 →「接口响应缺少内容」。
另有两点加重症状：15 秒超时对大预算生成偏紧；响应形状只认 content 字符串。

修复：
  ① AI.textOf()：兼容 content 字符串 / 数组分片 / reasoning_content / choices[0].text / output_text；
  ② 默认预算 360→900；超时 15s→20s（mt≥600 时 30s）；
  ③ 空内容自动重试一次（预算抬到 ≥1200、去掉 json）——把「思考吃光预算」这条最常见的死路走通；
  ④ 错误信息带上 finish_reason，便于下次定位；
  ⑤ AI.san 支持自定义上限，报纸/长文不再被 700 字截断。
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


# ═══════════ ① san 支持自定义上限 ═══════════
sub1("AI.san=function(t){t=String(t||'').replace(/[<>]/g,'').split(String.fromCharCode(13)).join('');const d=AI_NL+AI_NL,d3=d+AI_NL;while(t.indexOf(d3)>=0)t=t.split(d3).join(d);return t.trim().slice(0,700);};",
"""AI.san=function(t,max){t=String(t||'').replace(/[<>]/g,'').split(String.fromCharCode(13)).join('');const d=AI_NL+AI_NL,d3=d+AI_NL;while(t.indexOf(d3)>=0)t=t.split(d3).join(d);return t.trim().slice(0,Math.max(200,Number(max)||700));};   /* v4.20.2：报纸等长文可传自定义上限 */""", 'san 上限参数')

# ═══════════ ② 响应形状兼容 + finish_reason 诊断 ═══════════
sub1("""AI.ask=function(sys,user,opt){""",
"""/* v4.20.2：思考型模型的 content 可能为空、或在 reasoning_content/数组分片里——
 * 统一在 textOf 里兼容，避免「接口响应缺少内容」把能用的响应误判为失败 */
AI.textOf=function(j){
 try{
  const c=j&&j.choices&&j.choices[0],m=c&&c.message;
  const grab=function(x){
   if(!x)return '';
   if(typeof x==='string')return x;
   if(Array.isArray(x))return x.map(function(p){return (p&&(p.text||p.content))||'';}).join('');
   if(typeof x==='object')return String(x.text||x.content||'');
   return '';
  };
  let t=grab(m&&m.content);
  if(!t)t=grab(m&&m.reasoning_content);
  if(!t)t=grab(c&&c.text);
  if(!t)t=grab(j&&j.output_text);
  return String(t||'').trim();
 }catch(e){return '';}
};
AI.ask=function(sys,user,opt){""", 'textOf 兼容层')

# ═══════════ ③ 预算/超时提升 + 空内容自动重试 ═══════════
sub1("""AI.ask=function(sys,user,opt){
 return new Promise(function(res,rej){
  let done=false;const ctl=('AbortController' in window)?new AbortController():null;
  const tm=setTimeout(function(){if(done)return;done=true;try{if(ctl)ctl.abort();}catch(e){}rej(new Error('请求超时（15 秒）'));},15000);
  function fin(err,txt){if(done)return;done=true;clearTimeout(tm);if(err)rej(err);else res(txt);}
  let url=String(AI.cfg.url||'');
  while(url.slice(-1)==='/')url=url.slice(0,-1);
  url=url+'/chat/completions';
  fetch(url,{method:'POST',signal:ctl?ctl.signal:undefined,
   headers:{'Content-Type':'application/json','Authorization':'Bearer '+String(AI.cfg.key||'')},
   body:JSON.stringify({model:AI.cfg.model||'gpt-4o-mini',
    messages:[{role:'system',content:sys},{role:'user',content:user}],
    temperature:0.9,max_tokens:(opt&&opt.mt)||360,response_format:(opt&&opt.json)?{type:'json_object'}:undefined})})
  .then(function(r){
   if(!r.ok)return r.text().then(function(t){throw new Error('HTTP '+r.status+(t?(' · '+String(t).split(AI_NL).join(' ').slice(0,90)):''));});
   return r.json();
  })
  .then(function(j){
   const t=j&&j.choices&&j.choices[0]&&j.choices[0].message&&j.choices[0].message.content;
   if(!t)throw new Error('接口响应缺少内容（请确认是 OpenAI 兼容接口）');
   fin(null,String(t));
  })
  .catch(function(e){fin((e&&e.name==='AbortError')?new Error('请求超时（15 秒）'):e);});
 });
};""",
"""AI.ask=function(sys,user,opt){
 const mt0=(opt&&opt.mt)||900;                     /* v4.20.2：默认预算 360→900（思考型模型要留够正式内容的额度） */
 const toMs=mt0>=600?30000:20000;                  /* v4.20.2：超时 15s→20s（大预算 30s） */
 const attempt=function(mt,useJson){
  return new Promise(function(res,rej){
   let done=false;const ctl=('AbortController' in window)?new AbortController():null;
   const tm=setTimeout(function(){if(done)return;done=true;try{if(ctl)ctl.abort();}catch(e){}rej(new Error('请求超时（'+Math.round(toMs/1000)+' 秒）'));},toMs);
   function fin(err,txt){if(done)return;done=true;clearTimeout(tm);if(err)rej(err);else res(txt);}
   let url=String(AI.cfg.url||'');
   while(url.slice(-1)==='/')url=url.slice(0,-1);
   url=url+'/chat/completions';
   fetch(url,{method:'POST',signal:ctl?ctl.signal:undefined,
    headers:{'Content-Type':'application/json','Authorization':'Bearer '+String(AI.cfg.key||'')},
    body:JSON.stringify({model:AI.cfg.model||'gpt-4o-mini',
     messages:[{role:'system',content:sys},{role:'user',content:user}],
     temperature:0.9,max_tokens:mt,response_format:useJson?{type:'json_object'}:undefined})})
   .then(function(r){
    if(!r.ok)return r.text().then(function(t){throw new Error('HTTP '+r.status+(t?(' · '+String(t).split(AI_NL).join(' ').slice(0,90)):''));});
    return r.json();
   })
   .then(function(j){
    const t=AI.textOf(j);
    if(!t){
     let fr='?';
     try{fr=(j&&j.choices&&j.choices[0]&&j.choices[0].finish_reason)||'?';}catch(e){}
     throw new Error('接口响应缺少内容（finish_reason='+fr+'；推理模型可能把预算用在了思考上）');
    }
    fin(null,t);
   })
   .catch(function(e){fin((e&&e.name==='AbortError')?new Error('请求超时（'+Math.round(toMs/1000)+' 秒）'):e);});
  });
 };
 return attempt(mt0,!!(opt&&opt.json)).catch(function(e){
  const m=String((e&&e.message)||e);
  /* v4.20.2：空内容（多半是思考吃光预算）→ 抬预算、去掉 json 再试一次 */
  if(m.indexOf('缺少内容')>=0)return attempt(Math.max(1200,mt0*2),false);
  throw e;
 });
};""", '预算/超时/重试')


# ═══════════ ⑥ 长文清洗上限（报纸等多段输出）═══════════
sub1("""AI.ask(b.sys,b.user,{mt:900}).then(function(t){
  AI.busy=false;
  const txt=AI.san(t);""", """AI.ask(b.sys,b.user,{mt:900}).then(function(t){
  AI.busy=false;
  const txt=AI.san(t,1200);   /* v4.20.2：多段长文（报纸）不再被 700 字截断 */""", '报纸清洗上限')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('AI 兼容性修复已应用：%d -> %d 字符（%+d）' % (orig, len(s), len(s) - orig))
