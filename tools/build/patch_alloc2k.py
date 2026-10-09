# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 40：建档分配页 2K 式改版（v4.28.1）

【背景】用户反馈「分配初始属性改一下」。技能扩到 15 项后，分配页是 15 行单列——
  又长又挤，也看不出「我在塑造一个什么类型的球员」。对照 2K 的 MyPLAYER 建档：
  按大类分组、组内属性、实时总评——照此改版。

【改动】
  1. renderAllocRows 重写：15 项按六组分组（内线得分/外线投篮/组织传球/防守/篮板/
     身体素质），每组一张组卡（组名 + 实时小计），卡内属性行紧凑化（−/数值/+/条形）；
     桌面双列 grid、窄屏自动单列。
  2. 顶部新增「当前 OVR」实时预览（ovrPreview()：按分配值合成六大项 + 位置权重，
     身体基础按身高体重预估——和正式公式同源），加点立刻看到总评变化。
  3. 修正 confirmAlloc 漏网接点：身体素质初始值直接写 S.a.ath（v4.28.0 后是派生值，
     会被 syncFromSkills 覆盖丢失）→ 改写 S.a.athBase。
  边界：分配点数/基础值/上限数值不变；allocInc/Dec/Random/Reset 表驱动不动。
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


# ═══════════ 1. renderAlloc 顶部：OVR 实时预览 ═══════════
sub1("""   <div style="display:flex;justify-content:space-between;font-size:15px;font-weight:700">
    <span>可分配点数</span><span style="color:#ffb37a">${devOn?'∞（开发者模式）':allocLeft}</span>
   </div>""",
"""   <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:8px">
    <span style="font-size:13px;color:#aab2c5">当前 OVR（随分配实时变化 · 身体基础由身高体重决定）</span>
    <b id="ovrPreview" style="font-size:26px;color:#fbbf24">${ovrPreview()}</b>
   </div>
   <div style="display:flex;justify-content:space-between;font-size:15px;font-weight:700">
    <span>可分配点数</span><span style="color:#ffb37a">${devOn?'∞（开发者模式）':allocLeft}</span>
   </div>""", 'OVR 预览行')

# ═══════════ 2. ovrPreview + renderAllocRows 重写（2K 式分组） ═══════════
sub1("""function renderAllocRows(){
  const box=$('#allocRows');box.innerHTML='';
  SKILLS.forEach(([k,n])=>{
    const v=allocSkills[k];
    const row=document.createElement('div');
    row.style.cssText='display:flex;align-items:center;gap:8px;padding:8px 0;border-bottom:1px dashed #232c40';
    row.innerHTML=`<span style="width:44px;color:#aab2c5;font-size:13px">${n}</span>
     <button class="minirowbtn" onclick="allocInc('${k}')">+</button>
     <span style="min-width:36px;text-align:center;font-weight:800;color:${v>CFG.SKILL_BASE?'#ffb37a':'#fff'}">${v}</span>
     <button class="minirowbtn" onclick="allocDec('${k}')">−</button>
     <div style="flex:1"><div class="bar"><i style="width:${v}%"></i></div></div>`;
    box.appendChild(row);
  });
  const go=$('#allocGo');""",
"""/* v4.28.1：建档 OVR 实时预览——与正式公式同源（分配值合成六大项 + 位置权重；
 * 身体基础按身高体重预估，与 confirmAlloc 同式去随机），加点立刻看到总评变化 */
function ovrPreview(){
  const k=allocSkills,w=POS[S.pos].w;
  const inside=(k.finish||55)*.5+(k.dunk||55)*.5;
  const outside=(k.three||55)*.5+(k.mid||55)*.3+(k.free||55)*.2;
  const play=(k.handle||55)*.5+(k.pass||55)*.5;
  const def=(k.perdef||55)*.32+(k.steal||55)*.18+(k.intdef||55)*.28+(k.block||55)*.22;
  const reb=k.reb||55;
  const ab=clamp(Math.round(CFG.SKILL_BASE+(190-S.height)*.15-(S.weight-85)*.2),35,95);
  const ath=ab*.4+(k.speed||55)*.3+(k.strength||55)*.3;
  return Math.round(inside*w.inside+outside*w.outside+play*w.play+def*w.def+reb*w.reb+ath*w.ath);
}
function renderAllocRows(){
  const box=$('#allocRows');box.innerHTML='';
  /* v4.28.1：2K 式分组——六组组卡（组名+实时小计），桌面双列、窄屏单列 */
  const GROUPS=[
    ['🏀 内线得分',[['finish','终结'],['dunk','扣篮']]],
    ['🎯 外线投篮',[['three','三分'],['mid','中投'],['free','罚球']]],
    ['🧭 组织传球',[['handle','控球'],['pass','传球']]],
    ['🛡 防守',[['perdef','外防'],['steal','抢断'],['intdef','内防'],['block','盖帽']]],
    ['💪 篮板',[['reb','篮板']]],
    ['⚡ 身体素质',[['speed','速度'],['strength','力量']]]
  ];
  const wrap=document.createElement('div');
  wrap.style.cssText='display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:10px;margin:4px 0 8px';
  GROUPS.forEach(([g,items])=>{
    const card=document.createElement('div');
    card.style.cssText='border:1px solid #232c40;border-radius:10px;padding:10px 12px;background:rgba(255,255,255,.02)';
    const avg=Math.round(items.reduce((s,x)=>s+allocSkills[x[0]],0)/items.length);
    let h='<div style="display:flex;justify-content:space-between;margin-bottom:6px"><span style="font-size:13px;color:#ffd479">'+g+'</span><b style="font-size:13px;color:'+(avg>CFG.SKILL_BASE?'#ffb37a':'#aab2c5')+'">'+avg+'</b></div>';
    items.forEach(([k,n])=>{
      const v=allocSkills[k];
      h+='<div style="display:flex;align-items:center;gap:6px;padding:4px 0">'
        +'<span style="width:40px;color:#aab2c5;font-size:12px">'+n+'</span>'
        +'<button class="minirowbtn" onclick="allocDec(\\''+k+'\\')">−</button>'
        +'<span style="min-width:32px;text-align:center;font-weight:800;color:'+(v>CFG.SKILL_BASE?'#ffb37a':'#fff')+'">'+v+'</span>'
        +'<button class="minirowbtn" onclick="allocInc(\\''+k+'\\')">+</button>'
        +'<div style="flex:1"><div class="bar"><i style="width:'+v+'%"></i></div></div></div>';
    });
    card.innerHTML=h;wrap.appendChild(card);
  });
  box.appendChild(wrap);
  const op=$('#ovrPreview');if(op)op.textContent=ovrPreview();
  const go=$('#allocGo');""", 'renderAllocRows 分组版')

# ═══════════ 3. confirmAlloc：身体素质初始值 → athBase ═══════════
sub1("  S.a.ath=clamp(Math.round(CFG.SKILL_BASE+R.int(-4,8)+(190-S.height)*.15-(S.weight-85)*.2),35,95);",
     "  S.a.athBase=clamp(Math.round(CFG.SKILL_BASE+R.int(-4,8)+(190-S.height)*.15-(S.weight-85)*.2),35,95);   /* v4.28.1：athBase（原直接写派生值 S.a.ath 会被 syncFromSkills 覆盖丢失） */", 'confirmAlloc athBase')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('建档分配页 2K 改版已应用：%d -> %d 字符（%+d）' % (orig, len(s), len(s) - orig))
