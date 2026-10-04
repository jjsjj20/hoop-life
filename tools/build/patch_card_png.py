# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 14：P8 分享卡图片版（Canvas → PNG）（v4.15.0）

终章页在网页版分享卡旁新增「🖼 分享卡(PNG)」：
  · shareCardData()：纯函数数据模型（读 S，返回绘制所需的全量字段）——可测试；
  · drawShareCard(ctx,data)：程序化 Canvas 绘制（渐变底 / OVR 徽章 / 五项场均 /
    效力球队 / 得分曲线折线 / 荣誉墙 / 评语），零外部依赖、支持中文系统字体；
  · shareCardPNG()：toBlob 导出 PNG 下载；当前环境不支持画布/导出时
    自动回退网页版分享卡（jsdom 等无 canvas 环境不抛错）。
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


# ═══════════ 1. 终章页按钮：网页版旁加 PNG 版 ═══════════
sub1("""  <button class="btn" onclick="shareCardDL()">🖼 生成分享卡</button>""",
"""  <button class="btn" onclick="shareCardDL()">🖼 生成分享卡</button>
  <button class="btn" onclick="shareCardPNG()">🖼 分享卡(PNG)</button>""", '终章 PNG 按钮')

# ═══════════ 2. 数据模型 + Canvas 绘制 + 导出 ═══════════
FUNCS = """/* ── P8 图片版分享卡（v4.15）：Canvas 程序化绘制，导出 PNG ── */
function shareCardData(){
  const seas=(S.career&&S.career.seasons)||0;
  const avg=n=>seas?Math.round(n/seas*10)/10:0;
  let rv;try{rv=careerReview();}catch(e){rv={title:'🏀 篮球生涯',lines:['篮球记住了他来过。']};}
  return {name:S.name,pos:(POS[S.pos]||{}).n||'',league:S.league||'',
    era:(S.birthYear+15)+'–'+(S.birthYear+S.age),seasons:seas,
    peak:clamp(Math.round(S.peakO||ovr()),0,99),
    honorsN:(S.honors||[]).length,
    stats:{pts:avg(S.career.pts),reb:avg(S.career.reb),ast:avg(S.career.ast),stl:avg(S.career.stl||0),blk:avg(S.career.blk||0)},
    teams:(S.played&&S.played.length)?S.played.slice():[S.team||'—'],
    honors:(S.honors||[]).map(h=>h.t),
    rows:(S.history||[]).filter(h=>typeof h.ppg==='number').map(h=>({y:h.y||'',ppg:h.ppg})),
    review:rv};
}
function drawShareCard(ctx,d){
  const W=720,H=1140,M=36,GOLD='#fbbf24',DIM='#8fa0c4',WHITE='#ffffff';
  const bg=ctx.createLinearGradient(0,0,0,H);bg.addColorStop(0,'#101830');bg.addColorStop(1,'#0a0f1f');
  ctx.fillStyle=bg;ctx.fillRect(0,0,W,H);
  ctx.strokeStyle='#232c44';ctx.strokeRect(6,6,W-12,H-12);
  const wrap=(text,x,y,maxW,lh)=>{
    let line='',yy=y;
    for(const ch0 of String(text)){
      if(ctx.measureText(line+ch0).width>maxW){ctx.fillText(line,x,yy);yy+=lh;line=ch0;}
      else line+=ch0;
    }
    if(line)ctx.fillText(line,x,yy);return yy+lh;
  };
  /* 头部：OVR 徽章 + 名字 */
  ctx.beginPath();ctx.arc(M+46,96,42,0,Math.PI*2);
  ctx.fillStyle='#141d33';ctx.fill();ctx.strokeStyle=GOLD;ctx.lineWidth=2.5;ctx.stroke();
  ctx.fillStyle=GOLD;ctx.font='bold 26px system-ui,"PingFang SC","Microsoft YaHei",sans-serif';ctx.textAlign='center';
  ctx.fillText(String(d.peak),M+46,104);
  ctx.font='10px system-ui,sans-serif';ctx.fillStyle=DIM;ctx.fillText('最高OVR',M+46,120);
  ctx.textAlign='left';
  ctx.fillStyle=WHITE;ctx.font='bold 34px system-ui,"PingFang SC","Microsoft YaHei",sans-serif';ctx.fillText(d.name,M+110,86);
  ctx.fillStyle=DIM;ctx.font='15px system-ui,"PingFang SC",sans-serif';
  ctx.fillText(d.pos+' · '+d.seasons+' 个赛季 · '+d.honorsN+' 项荣誉',M+110,114);
  ctx.fillStyle=GOLD;ctx.font='13px system-ui,"PingFang SC",sans-serif';
  ctx.fillText('篮球生涯 '+d.era+' · '+d.league,M+110,138);
  ctx.strokeStyle='#232c44';ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(M,168);ctx.lineTo(W-M,168);ctx.stroke();
  /* 五项场均 */
  const labs=['场均得分','场均篮板','场均助攻','场均抢断','场均盖帽'];
  const keys=['pts','reb','ast','stl','blk'];
  const bw=(W-M*2-16)/5;
  keys.forEach((k,i)=>{
    const x=M+i*(bw+4);
    ctx.fillStyle='#0c1326';ctx.fillRect(x,186,bw,70);
    ctx.strokeStyle='#1e2740';ctx.strokeRect(x,186,bw,70);
    ctx.fillStyle=WHITE;ctx.font='bold 21px system-ui,sans-serif';ctx.textAlign='center';
    ctx.fillText(String(d.stats[k]),x+bw/2,220);
    ctx.fillStyle=DIM;ctx.font='11px system-ui,"PingFang SC",sans-serif';ctx.fillText(labs[i],x+bw/2,242);
    ctx.textAlign='left';
  });
  /* 效力球队 */
  ctx.fillStyle=DIM;ctx.font='12px system-ui,"PingFang SC",sans-serif';ctx.fillText('效力球队',M,288);
  ctx.fillStyle='#cfe0ff';ctx.font='14px system-ui,"PingFang SC",sans-serif';
  let ty=wrap(d.teams.join('  ➔  '),M,310,W-M*2,22);
  /* 得分曲线 */
  ctx.fillStyle=DIM;ctx.font='12px system-ui,"PingFang SC",sans-serif';ctx.fillText('生涯场均得分曲线',M,ty+12);
  if(d.rows.length>1){
    const gx=M,gy=ty+30,gw=W-M*2,gh=110;
    const mx=Math.max(10,...d.rows.map(r=>r.ppg))*1.15;
    const px=i=>gx+i*gw/(d.rows.length-1);
    const py=v=>gy+gh-(v/mx)*gh;
    ctx.strokeStyle='#28324a';ctx.beginPath();ctx.moveTo(gx,gy+gh);ctx.lineTo(gx+gw,gy+gh);ctx.stroke();
    ctx.strokeStyle='#fbbf24';ctx.lineWidth=2.4;ctx.beginPath();
    d.rows.forEach((r,i)=>{i?ctx.lineTo(px(i),py(r.ppg)):ctx.moveTo(px(i),py(r.ppg));});
    ctx.stroke();
    ctx.fillStyle=GOLD;
    d.rows.forEach((r,i)=>{ctx.beginPath();ctx.arc(px(i),py(r.ppg),3.4,0,Math.PI*2);ctx.fill();});
    ctx.fillStyle=DIM;ctx.font='11px system-ui,sans-serif';
    ctx.fillText(d.rows[0].y,gx,gy+gh+18);
    const last=d.rows[d.rows.length-1];
    ctx.fillText(last.y,gx+gw-ctx.measureText(last.y).width,gy+gh+18);
    ty=gy+gh+34;
  }else{
    ctx.fillStyle=DIM;ctx.fillText('没有逐季数据可画',M,ty+34);ty=ty+46;
  }
  /* 荣誉墙 */
  ctx.fillStyle=DIM;ctx.font='12px system-ui,"PingFang SC",sans-serif';ctx.fillText('荣誉墙（'+d.honorsN+'）',M,ty+14);
  ctx.font='13px system-ui,"PingFang SC",sans-serif';
  let hy=wrap(d.honors.length?('🏅 '+d.honors.join('  🏅 ')):'荣誉墙虚位以待',M,ty+40,W-M*2,22);
  /* 评语 */
  ctx.fillStyle='#fb923c';ctx.font='bold 15px system-ui,"PingFang SC",sans-serif';
  ctx.fillText(rvText(d.review),M,hy+26);
  ctx.fillStyle='#c9d4ec';ctx.font='14px system-ui,"PingFang SC",sans-serif';
  hy=wrap(d.review.lines[0]||'',M,hy+52,W-M*2,22);
  /* 页脚 */
  ctx.fillStyle='#4a5a80';ctx.font='11px system-ui,sans-serif';ctx.textAlign='center';
  ctx.fillText('篮球人生 · 生涯模拟 · 图片分享卡',W/2,H-24);ctx.textAlign='left';
}
function rvText(d){return d&&d.title?d.title:'🏀 篮球生涯';}
function shareCardPNG(){
  try{
    const data=shareCardData();
    const cv=document.createElement('canvas');cv.width=720;cv.height=1140;
    const ctx=cv.getContext?cv.getContext('2d'):null;
    if(!ctx){toast('当前环境不支持画布，已生成网页版分享卡');shareCardDL();return 'html';}
    drawShareCard(ctx,data);
    if(!cv.toBlob){toast('当前环境不支持图片导出，已生成网页版分享卡');shareCardDL();return 'html';}
    cv.toBlob(function(b){
      if(!b){shareCardDL();return;}
      const a=document.createElement('a');a.href=URL.createObjectURL(b);
      a.download='篮球人生分享卡-'+data.name+'.png';
      document.body.appendChild(a);a.click();document.body.removeChild(a);
      setTimeout(function(){try{URL.revokeObjectURL(a.href);}catch(e){}},1500);
      toast('📸 PNG 分享卡已生成');
      S.log=S.log||[];S.log.push({y:seasonLabel(),t:'生成了 PNG 分享卡'});
    },'image/png');
    return 'png';
  }catch(e){try{toast('生成失败：'+(e&&e.message||e));}catch(_){ } return 'err';}
}"""
sub1("""    S.log=S.log||[];S.log.push({y:seasonLabel(),t:'生成了生涯分享卡'});
  }catch(e){try{toast('生成失败：'+(e&&e.message||e));}catch(_){}}
}""",
"""    S.log=S.log||[];S.log.push({y:seasonLabel(),t:'生成了生涯分享卡'});
  }catch(e){try{toast('生成失败：'+(e&&e.message||e));}catch(_){}}
}
""" + FUNCS, 'PNG 分享卡三函数插入')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('P8 分享卡图片版已应用：%d -> %d 字符（%+d）' % (orig, len(s), len(s) - orig))
