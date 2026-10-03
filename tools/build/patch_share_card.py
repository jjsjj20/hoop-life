# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 11：生涯分享卡（P3.2 / v4.11.0）

退役终章页新增「生成分享卡」：把生涯总结渲染成一张自包含的单文件 HTML
（零外部依赖——不引字体、不引图片、不引脚本文件，另存到手机电脑都能直接打开）。
内容：姓名/位置/生涯跨度、最高 OVR、生涯场均五项、效力球队路径、
逐季场均得分曲线（内联 SVG）、荣誉墙、生涯评语。

可测试性：shareCardHTML() 是纯函数（读 S，返回字符串），测试用 jsdom 断言
关键数字与 S 一致、且不含任何外部引用；分享卡按钮由 showEnd 渲染可断言存在。
"""
import os

BASE = os.path.dirname(os.path.abspath(__file__))
HTML = os.environ.get('GAME_HTML') or os.path.join(BASE, '..', 'output', '篮球人生.html')

s = open(HTML, encoding='utf-8').read()
orig = len(s)


def sub1(old, new, why):
    n = s.count(old)
    if n != 1:
        raise SystemExit('!! %s 匹配 %d 次（期望 1）' % (why, n))
    return s.replace(old, new)


# ═══════════ 1. 生成器 + 下载（挂在 endNow 之后）═══════════
FUNC = """function endNow(){if(confirm('确定提前结束当前生涯吗？（将进入生涯总结）')){S.retired=true;UI={mode:'end'};save();showEnd();}}
/* ── 生涯分享卡（v4.11 P3.2）：自包含单文件，另存即可分享 ── */
function shareCardHTML(){
  const seas=(S.career&&S.career.seasons)||0;
  const avg=n=>seas?Math.round(n/seas*10)/10:0;
  const hs=(S.honors||[]).map(h=>h.t);
  const teams=(S.played||[]).slice();
  const rv=(()=>{try{return careerReview();}catch(e){return {title:'🏀 篮球生涯',lines:['篮球记住了他来过。']};}})();
  const rows=(S.history||[]).filter(h=>typeof h.ppg==='number');
  const cw=640,chh=180,cp=40;
  const vals=rows.map(h=>h.ppg);
  const mx=Math.max(10,...vals)*1.15;
  const px=i=>rows.length>1?(cp+i*(cw-cp*2)/(rows.length-1)):cw/2;
  const py=v=>chh-cp-(v/mx)*(chh-cp*2);
  const line=vals.map((v,i)=>px(i).toFixed(1)+','+py(v).toFixed(1)).join(' ');
  const area=vals.length?(cp+','+(chh-cp)+' '+line+' '+(rows.length>1?px(vals.length-1).toFixed(1):cw/2)+','+(chh-cp)):'';
  const dots=vals.map((v,i)=>'<circle cx="'+px(i).toFixed(1)+'" cy="'+py(v).toFixed(1)+'" r="3.4" fill="#fbbf24"><title>'+esc(rows[i].y||'')+' · 场均 '+v+' 分</title></circle>').join('');
  const chips=hs.length?hs.slice(0,16).map(t=>'<span class="hb">'+esc(t)+'</span>').join(''):'<span class="hb dim">荣誉墙虚位以待</span>';
  const moreN=hs.length>16?'<span class="hb dim">…等 '+hs.length+' 项</span>':'';
  const teamChips=teams.length?teams.map(t=>'<span class="tb">'+esc(t)+'</span>').join('<span class="arr">➔</span>'):'<span class="tb">'+esc(S.team||'—')+'</span>';
  const curve=rows.length
    ?'<svg viewBox="0 0 '+cw+' '+chh+'" preserveAspectRatio="none" role="img" aria-label="生涯场均得分曲线">'
     +'<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fbbf24" stop-opacity=".28"/><stop offset="1" stop-color="#fbbf24" stop-opacity="0"/></linearGradient></defs>'
     +'<line x1="'+cp+'" y1="'+(py(0)+1).toFixed(1)+'" x2="'+(cw-cp)+'" y2="'+(py(0)+1).toFixed(1)+'" stroke="#28324a" stroke-width="1"/>'
     +'<line x1="'+cp+'" y1="'+py(mx/1.15).toFixed(1)+'" x2="'+(cw-cp)+'" y2="'+py(mx/1.15).toFixed(1)+'" stroke="#1c2438" stroke-width="1" stroke-dasharray="4 5"/>'
     +'<text x="'+(cw-cp)+'" y="'+(py(mx/1.15)-6).toFixed(1)+'" text-anchor="end" fill="#5b6784" font-size="11">'+(Math.round(mx/1.15*10)/10)+' 分</text>'
     +(area?'<polygon points="'+area+'" fill="url(#g)"/>':'')
     +(line?'<polyline points="'+line+'" fill="none" stroke="#fbbf24" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"/>':'')
     +dots+'</svg>'
    :'<div class="mini">没有逐季数据可画——生涯太短，或存档来自没有曲线记录的老版本。</div>';
  return '<!DOCTYPE html>\\n<html lang="zh-CN">\\n<head>\\n<meta charset="utf-8">\\n<meta name="viewport" content="width=device-width,initial-scale=1">\\n'
    +'<title>'+esc(S.name)+' · 篮球人生分享卡</title>\\n'
    +'<style>\\n'
    +'body{margin:0;padding:24px 12px;background:#070b16;font-family:system-ui,-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;color:#e8edf7;}\\n'
    +'.card{max-width:680px;margin:0 auto;background:linear-gradient(160deg,#101830,#0a0f1f 60%);border:1px solid #232c44;border-radius:18px;padding:26px 26px 18px;box-shadow:0 18px 50px rgba(0,0,0,.5)}\\n'
    +'.head{display:flex;gap:18px;align-items:center;border-bottom:1px solid #232c44;padding-bottom:16px}\\n'
    +'.ovr{width:74px;height:74px;border-radius:50%;background:radial-gradient(circle at 32% 28%,#2a3a63,#141d33);border:2px solid #fbbf24;display:flex;flex-direction:column;align-items:center;justify-content:center;flex:none}\\n'
    +'.ovr b{font-size:26px;color:#fbbf24;line-height:1}.ovr span{font-size:10px;color:#8fa0c4;letter-spacing:2px;margin-top:3px}\\n'
    +'h1{margin:0;font-size:26px;letter-spacing:1px}.sub{color:#8fa0c4;font-size:13px;margin-top:5px}\\n'
    +'.era{color:#fbbf24;font-size:12px;margin-top:3px}\\n'
    +'.grid{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin:16px 0}\\n'
    +'.stat{background:#0c1326;border:1px solid #1e2740;border-radius:10px;padding:10px 4px;text-align:center}\\n'
    +'.stat b{display:block;font-size:20px;color:#fff}.stat span{font-size:11px;color:#8fa0c4}\\n'
    +'.sec{font-size:12px;color:#8fa0c4;letter-spacing:2px;margin:16px 0 8px}\\n'
    +'.teams{display:flex;flex-wrap:wrap;gap:6px;align-items:center}\\n'
    +'.tb{background:#12203c;border:1px solid #24406e;color:#cfe0ff;font-size:12px;padding:4px 9px;border-radius:999px}\\n'
    +'.arr{color:#4a5a80;font-size:12px}\\n'
    +'.hl{display:flex;flex-wrap:wrap;gap:6px}\\n'
    +'.hb{background:#241d08;border:1px solid #4d3d10;color:#fbbf24;font-size:12px;padding:4px 9px;border-radius:999px}\\n'
    +'.hb.dim{background:#111a2c;color:#5b6784;border-color:#232c44}\\n'
    +'.quote{margin-top:16px;background:#0c1326;border-left:3px solid #f97316;border-radius:0 10px 10px 0;padding:12px 14px}\\n'
    +'.quote b{color:#fb923c}.quote p{margin:6px 0 0;color:#c9d4ec;font-size:14px;line-height:1.7}\\n'
    +'.mini{color:#5b6784;font-size:12px}\\n'
    +'.foot{margin-top:18px;padding-top:12px;border-top:1px solid #1e2740;color:#4a5a80;font-size:11px;text-align:center;letter-spacing:1px}\\n'
    +'</style>\\n</head>\\n<body>\\n'
    +'<div class="card">\\n'
    +'<div class="head"><div class="ovr"><b>'+clamp(Math.round(S.peakO||ovr()),0,99)+'</b><span>最高OVR</span></div>'
    +'<div><h1>'+esc(S.name)+'</h1>'
    +'<div class="sub">'+esc(POS[S.pos].n)+' · '+(seas||'0')+' 个赛季 · '+(hs.length)+' 项荣誉</div>'
    +'<div class="era">篮球生涯 '+(S.birthYear+15)+'–'+(S.birthYear+S.age)+' · '+esc(S.league||'')+'</div></div></div>\\n'
    +'<div class="grid">'
    +'<div class="stat"><b>'+avg(S.career.pts)+'</b><span>场均得分</span></div>'
    +'<div class="stat"><b>'+avg(S.career.reb)+'</b><span>场均篮板</span></div>'
    +'<div class="stat"><b>'+avg(S.career.ast)+'</b><span>场均助攻</span></div>'
    +'<div class="stat"><b>'+avg(S.career.stl||0)+'</b><span>场均抢断</span></div>'
    +'<div class="stat"><b>'+avg(S.career.blk||0)+'</b><span>场均盖帽</span></div>'
    +'</div>\\n'
    +'<div class="sec">效力球队</div><div class="teams">'+teamChips+'</div>\\n'
    +'<div class="sec">生涯场均得分曲线</div>'+curve+'\\n'
    +'<div class="sec">荣誉墙</div><div class="hl">'+chips+moreN+'</div>\\n'
    +'<div class="quote"><b>'+esc(rv.title)+'</b><p>'+esc(rv.lines[0]||'')+'</p></div>\\n'
    +'<div class="foot">篮球人生 · 生涯模拟 · 单文件分享卡</div>\\n'
    +'</div>\\n</body>\\n</html>';
}
function shareCardDL(){
  try{
    const html=shareCardHTML();
    const blob=new Blob([html],{type:'text/html;charset=utf-8'});
    const a=document.createElement('a');
    a.href=URL.createObjectURL(blob);
    a.download='篮球人生分享卡-'+S.name+'.html';
    document.body.appendChild(a);a.click();document.body.removeChild(a);
    setTimeout(function(){try{URL.revokeObjectURL(a.href);}catch(e){}},1500);
    toast('📸 分享卡已生成——单文件 HTML，手机电脑都能直接打开');
    S.log=S.log||[];S.log.push({y:seasonLabel(),t:'生成了生涯分享卡'});
  }catch(e){try{toast('生成失败：'+(e&&e.message||e));}catch(_){}}
}"""
s = sub1("function endNow(){if(confirm('确定提前结束当前生涯吗？（将进入生涯总结）')){S.retired=true;UI={mode:'end'};save();showEnd();}}",
         FUNC, '分享卡生成器插入')

# ═══════════ 2. 终章页按钮 ═══════════
s = sub1("""  html+=`<button class="btn ghost" onclick="showArchive()">📋 查看完整档案</button>
  <button class="btn" onclick="renderMenu()">↩ 回到主菜单</button>`;""",
"""  html+=`<button class="btn ghost" onclick="showArchive()">📋 查看完整档案</button>
  <button class="btn" onclick="shareCardDL()">🖼 生成分享卡</button>
  <button class="btn" onclick="renderMenu()">↩ 回到主菜单</button>`;""", '终章页分享卡按钮')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('分享卡已应用：%d -> %d 字符（%+d）' % (orig, len(s), len(s) - orig))
