# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 42：能力雷达改六大项（v4.28.3）

【背景】用户反馈「能力雷达改一下」。档案页雷达原画 15 项细分属性——
  15 个轴挤在 280×240 的图里，间隔仅 24°，标签互相重叠难读；
  且 15 项明细就在右侧清单与「📊 属性」面板里，雷达再画一遍是重复。
  改为**六大项雷达**（内线/外线/组织/防守/篮板/身体）：6 轴清晰、
  与结果页概览/📊 属性/分配页的口径完全统一；15 项明细保留在右侧清单。

【改动】
  1. radarSVG 加 keys 参数：传 COMPONENTS 时按六大项画（数值源 S.a，
     中文短标签 内线/外线/组织/防守/篮板/身体）；不传保持原 15 项行为。
  2. showArchive 调用点传 COMPONENTS；标签改「能力雷达（六大项）」。
  边界：radarSVG 其他调用点不受影响（默认参数=旧行为）。
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


# ═══════════ 1. radarSVG 支持 keys 参数（六大项模式） ═══════════
sub1("""function radarSVG(w,h,labels){
  const n=SKILLS.length,cx=w/2,cy=h/2,R=Math.min(w,h)/2-(labels?26:12);
  const pt=(i,r)=>{const a=-Math.PI/2+i*2*Math.PI/n;
    return [cx+Math.cos(a)*r,cy+Math.sin(a)*r];};
  const poly=rs=>rs.map((r,i)=>pt(i,r).map(v=>v.toFixed(1)).join(',')).join(' ');
  let g='';
  [.25,.5,.75,1].forEach(k=>{g+=`<polygon points="${poly(new Array(n).fill(R*k))}" fill="none" stroke="#222b3f" stroke-width="1"/>`;});
  for(let i=0;i<n;i++){const[x,y]=pt(i,R);
    g+=`<line x1="${cx}" y1="${cy}" x2="${x.toFixed(1)}" y2="${y.toFixed(1)}" stroke="#1a2130" stroke-width="1"/>`;}
  const rs=SKILLS.map(([k])=>R*clamp((S.skills&&S.skills[k])||0,0,99)/99);
  g+=`<polygon points="${poly(rs)}" fill="rgba(249,115,22,.26)" stroke="#f97316" stroke-width="2" stroke-linejoin="round"/>`;
  SKILLS.forEach(([k],i)=>{const[x,y]=pt(i,rs[i]);
    g+=`<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="2.3" fill="#ffb37a"/>`;});
  if(labels)SKILLS.forEach(([k,nm],i)=>{const[x,y]=pt(i,R+13);
    g+=`<text x="${x.toFixed(1)}" y="${(y+3.4).toFixed(1)}" text-anchor="middle" font-size="10" fill="#8b93a7">${esc(nm)}</text>`;});
  return `<svg class="radar" viewBox="0 0 ${w} ${h}" width="${w}" height="${h}" aria-hidden="true">${g}</svg>`;
}""",
"""function radarSVG(w,h,labels,keys){
  /* v4.28.3：keys 传入六大项键（COMPONENTS）时按六大项画（数值源 S.a、中文短标签）——
   * 15 项细项雷达轴距仅 24°、标签重叠难读，且明细已在右侧清单/📊 属性；
   * 不传 keys 保持原 15 项行为（表驱动）。 */
  const CN={inside:'内线',outside:'外线',play:'组织',def:'防守',reb:'篮板',ath:'身体'};
  const items=keys?keys.map(k=>[k,CN[k]||k]):SKILLS;
  const n=items.length,cx=w/2,cy=h/2,R=Math.min(w,h)/2-(labels?26:12);
  const pt=(i,r)=>{const a=-Math.PI/2+i*2*Math.PI/n;
    return [cx+Math.cos(a)*r,cy+Math.sin(a)*r];};
  const poly=rs=>rs.map((r,i)=>pt(i,r).map(v=>v.toFixed(1)).join(',')).join(' ');
  let g='';
  [.25,.5,.75,1].forEach(k=>{g+=`<polygon points="${poly(new Array(n).fill(R*k))}" fill="none" stroke="#222b3f" stroke-width="1"/>`;});
  for(let i=0;i<n;i++){const[x,y]=pt(i,R);
    g+=`<line x1="${cx}" y1="${cy}" x2="${x.toFixed(1)}" y2="${y.toFixed(1)}" stroke="#1a2130" stroke-width="1"/>`;}
  const rs=items.map(([k])=>R*clamp((keys?(S.a&&S.a[k])||0:(S.skills&&S.skills[k])||0),0,99)/99);
  g+=`<polygon points="${poly(rs)}" fill="rgba(249,115,22,.26)" stroke="#f97316" stroke-width="2" stroke-linejoin="round"/>`;
  items.forEach(([k],i)=>{const[x,y]=pt(i,rs[i]);
    g+=`<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="2.3" fill="#ffb37a"/>`;});
  if(labels)items.forEach(([k,nm],i)=>{const[x,y]=pt(i,R+13);
    g+=`<text x="${x.toFixed(1)}" y="${(y+3.4).toFixed(1)}" text-anchor="middle" font-size="10" fill="#8b93a7">${esc(nm)}</text>`;});
  return `<svg class="radar" viewBox="0 0 ${w} ${h}" width="${w}" height="${h}" aria-hidden="true">${g}</svg>`;
}""", 'radarSVG keys 参数')

# ═══════════ 2. showArchive 调用点：六大项雷达 ═══════════
sub1("""  h+=`<label>🕸 能力雷达（15 项）</label><div class="radwrap">
   <div class="radcol">${radarSVG(280,240,true)}</div>""",
"""  h+=`<label>🕸 能力雷达（六大项 · 细分见右）</label><div class="radwrap">
   <div class="radcol">${radarSVG(280,240,true,COMPONENTS)}</div>""", '档案雷达六大项')

# ═══════════ 3. 赛季总结页雷达：同步六大项 ═══════════
sub1("   <div class=\"summ\"><h3>🕸 能力雷达</h3>${radarSVG(258,232,true)}</div>",
     "   <div class=\"summ\"><h3>🕸 能力雷达（六大项）</h3>${radarSVG(258,232,true,COMPONENTS)}</div>", '赛季总结雷达六大项')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('能力雷达改六大项已应用：%d -> %d 字符（%+d）' % (orig, len(s), len(s) - orig))
