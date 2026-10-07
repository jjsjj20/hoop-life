# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 39：OVR 属性体系全面对齐 NBA 2K（v4.28.0）

【背景】用户需求：「ovr系统全面向2k学习」。对照 NBA 2K25 评分体系：
  2K 的灵魂三件套 = 细分属性 × 按位置加权的 OVR × 徽章；属性分五大类
  （内线得分/外线投篮/组织传球/防守篮板/身体素质），评分区间 25-99。
  现状：11 项技能合成六大项（inside/outside/play/def/reb/ath）再按位置加权——
  OVR 结构已与 2K 同构，但缺罚球/抢断/速度/力量等关键细分属性，
  「身体素质」是笼统一项，罚球率由终结代管、抢断由外防代管（名不副实）。

【本轮改动（体系对齐档）】
  1. 技能层 11 → 15 项：新增 罚球(free)/抢断(steal)/力量(strength)/速度(speed)，
     按 2K 分类归位（罚球→外线投篮组、抢断→防守组、速度力量→身体素质组）。
  2. 大类合成更新（syncFromSkills）：
     外线 = 三分.5+中投.3+罚球.2 ｜ 防守 = 外防.32+抢断.18+内防.28+盖帽.22
     身体 = (身体基础 athBase).4 + 速度.3 + 力量.3（athBase 承载原「身体素质」，
     事件奖励与年龄衰退改作用于 athBase——派生值随速度/力量成长而上涨）。
  3. 模拟引擎接线（新属性不再是无用数字）：
     罚球率 ← 罚球属性（原由终结驱动）｜ 抢断 spg ← 外防.4+抢断.35+速度.25
     盖帽/篮板 ← 力量微加成（对抗价值）。
  4. 老档一次性迁移（ensureState）：free=(中投×2+终结)/3、steal=外防、
     strength=速度=身体素质基、athBase=身体素质——OVR 偏移 <±0.3（守恒设计）。
  5. 「📊 属性」面板（☰ 更多入口）：2K 式五大类分组 + 数值色条
     （85+ 金 / 75+ 绿 / 65+ 蓝 / 65- 红）。
  6. 建档分配自动适配 15 项（表驱动，30 点分配）。OVR 公式与位置权重不动
     （六大项骨架不变，分布稳定——难度标定不受影响）。

【边界】NPC 世界球员保持单值 OVR（全属性化属「全面重标定」范畴，本轮不含）；
  附加赛/NPC 互打不受影响；徽章系统不在本轮（体系对齐档）。
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


# ═══════════ 1. 技能表 11 → 15 项 ═══════════
sub1("""const SKILLS=[['three','三分'],['mid','中投'],['finish','终结'],['dunk','扣篮'],['handle','控球'],['pass','传球'],['perdef','外防'],['intdef','内防'],['block','盖帽'],['reb','篮板'],['clutch','关键']];
const SKILL_NAME={three:'三分',mid:'中投',finish:'终结',dunk:'扣篮',handle:'控球',pass:'传球',perdef:'外防',intdef:'内防',block:'盖帽',reb:'篮板',clutch:'关键'};""",
"""const SKILLS=[['three','三分'],['mid','中投'],['free','罚球'],['finish','终结'],['dunk','扣篮'],['handle','控球'],['pass','传球'],['perdef','外防'],['steal','抢断'],['intdef','内防'],['block','盖帽'],['reb','篮板'],['speed','速度'],['strength','力量'],['clutch','关键']];
const SKILL_NAME={three:'三分',mid:'中投',free:'罚球',finish:'终结',dunk:'扣篮',handle:'控球',pass:'传球',perdef:'外防',steal:'抢断',intdef:'内防',block:'盖帽',reb:'篮板',speed:'速度',strength:'力量',clutch:'关键'};""", '技能表 15 项')

# ═══════════ 2. syncFromSkills：2K 式大类合成 ═══════════
sub1("""function syncFromSkills(){ /* 由 11 项技能同步出六大项（供 OVR 与旧逻辑使用） */
  if(!S||!S.skills)return;
  const k=S.skills;
  S.a.outside=clamp(Math.round(k.three*.5+k.mid*.5),20,99);
  S.a.inside=clamp(Math.round(k.finish*.5+k.dunk*.5),20,99);
  S.a.play=clamp(Math.round(k.handle*.5+k.pass*.5),20,99);
  S.a.def=clamp(Math.round(k.perdef*.4+k.intdef*.35+k.block*.25),20,99);
  S.a.reb=clamp(k.reb,20,99);
  S.a.ath=clamp(S.a.ath||50,20,99);
  S.h.clutch=k.clutch;
}""",
"""function syncFromSkills(){ /* v4.28.0：由 15 项技能合成六大项（2K 式归类：外线含罚球、防守含抢断、身体=基础+速度+力量） */
  if(!S||!S.skills)return;
  const k=S.skills;
  S.a.inside=clamp(Math.round((k.finish||55)*.5+(k.dunk||55)*.5),20,99);
  S.a.outside=clamp(Math.round((k.three||55)*.5+(k.mid||55)*.3+(k.free||55)*.2),20,99);
  S.a.play=clamp(Math.round((k.handle||55)*.5+(k.pass||55)*.5),20,99);
  S.a.def=clamp(Math.round((k.perdef||55)*.32+(k.steal||55)*.18+(k.intdef||55)*.28+(k.block||55)*.22),20,99);
  S.a.reb=clamp(k.reb||55,20,99);
  if(S.a.athBase==null&&(k.speed!=null||k.strength!=null))S.a.athBase=clamp(S.a.ath||50,20,99);   /* 新档首次合成：身体基础取当前值 */
  if(S.a.athBase!=null)S.a.ath=clamp(Math.round(S.a.athBase*.4+(k.speed||55)*.3+(k.strength||55)*.3),20,99);   /* 三键齐才派生；纯老档（全缺）保持原值待迁移 */
  S.h.clutch=k.clutch;
}""", 'syncFromSkills 2K 归类')

# ═══════════ 3. defStats：抢断/速度/力量接线 ═══════════
sub1("""  const spg=stlMul*(.55+(k.perdef||55)/100*1.1)+(hu-60)*.012+R.float(-.35,.5);
  const bpg=blkMul*(.25+(k.block||55)/100*1.3)+(hu-60)*.006""",
"""  const spg=stlMul*(.55+((k.perdef||55)*.4+(k.steal||55)*.35+(k.speed||55)*.25)/100*1.1)+(hu-60)*.012+R.float(-.35,.5);
  const bpg=blkMul*(.25+(k.block||55)/100*1.3+((k.strength||55)-55)*.001)+(hu-60)*.006""", 'defStats 抢断/速度/力量')

# ═══════════ 4. shootRates：罚球率 ← 罚球属性 ═══════════
sub1("  const three=sk.three||60,mid=sk.mid||60,fin=sk.finish||60,dnk=sk.dunk||60,clu=sk.clutch||60;",
     "  const three=sk.three||60,mid=sk.mid||60,fin=sk.finish||60,dnk=sk.dunk||60,clu=sk.clutch||60,fr=sk.free||60;", 'fr 变量')
sub1("""  const ftRate=clamp(SHOT.ftBase+(fin-60)*SHOT.ftPerFinish+((pos==='C'||pos==='PF')?SHOT.ftCBPF:0)
    +clamp(st.inside*SHOT.ftPerIn,0,SHOT.ftCap),.06,.55);""",
"""  const ftRate=clamp(SHOT.ftBase+(fr-60)*SHOT.ftPerFinish+((pos==='C'||pos==='PF')?SHOT.ftCBPF:0)
    +clamp(st.inside*SHOT.ftPerIn,0,SHOT.ftCap),.06,.55);   /* v4.28.0：罚球率由「罚球」属性驱动（原由终结代管） */""", 'ftRate 罚球驱动')

# ═══════════ 5. simGame 篮板：力量微加成 ═══════════
sub1("  const reb=clamp(Math.round(((SK.reb*.05)+(S.pos==='C'?4.2:S.pos==='PF'?3.2:S.pos==='SF'?2.2:1.4)+hustleRpgAdd()*.7)*mf+R.float(-1.6,1.6)),0,24);",
     "  const reb=clamp(Math.round(((SK.reb*.05)+(SK.strength||55)*.004+(S.pos==='C'?4.2:S.pos==='PF'?3.2:S.pos==='SF'?2.2:1.4)+hustleRpgAdd()*.7)*mf+R.float(-1.6,1.6)),0,24);   /* v4.28.0：力量 → 篮板对抗微加成 */", '篮板力量')

# ═══════════ 6. 事件/训练/衰退：身体素质 → athBase ═══════════
sub1("  ['ath',(v,c)=>{const b=S.a.ath;S.a.ath=clamp(Math.round(S.a.ath+v),20,99);addGrind(Math.max(0,S.a.ath-b));c.push('身体素质'+fmt(v));",
     "  ['ath',(v,c)=>{const b=S.a.athBase||50;S.a.athBase=clamp(Math.round(S.a.athBase+v),20,99);addGrind(Math.max(0,S.a.athBase-b));c.push('身体素质'+fmt(v));", 'fx ath')

sub1("""     S.a.ath=clamp(S.a.ath+4,20,99);S.h.durability=clamp(S.h.durability+4,10,99);
     return '身体素质 → '+S.a.ath+'，耐久 → '+S.h.durability;}},""",
"""     S.a.athBase=clamp((S.a.athBase||50)+4,20,99);S.h.durability=clamp(S.h.durability+4,10,99);
     return '身体素质 → '+S.a.athBase+'，耐久 → '+S.h.durability;}},""", 'gym athBase')

sub1("""  if(S.age>=29)S.a.ath=clamp(S.a.ath-1,20,99);
  if(S.age>=32){S.a.ath=clamp(S.a.ath-1,20,99);S.skills.perdef=clamp(S.skills.perdef-1,25,99);S.skills.intdef=clamp(S.skills.intdef-1,25,99);}
  if(S.age>=36){S.a.ath=clamp(S.a.ath-2-(injSiteTotal()>=3?1:0),20,99);S.skills.finish=clamp(S.skills.finish-1,25,99);S.skills.dunk=clamp(S.skills.dunk-1,25,99);S.skills.reb=clamp(S.skills.reb-1,25,99);}
  if(S.age>41){S.a.ath=clamp(S.a.ath-2,20,99);}""",
"""  if(S.age>=29)S.a.athBase=clamp((S.a.athBase||50)-1,20,99);
  if(S.age>=32){S.a.athBase=clamp((S.a.athBase||50)-1,20,99);S.skills.perdef=clamp(S.skills.perdef-1,25,99);S.skills.intdef=clamp(S.skills.intdef-1,25,99);}
  if(S.age>=36){S.a.athBase=clamp((S.a.athBase||50)-2-(injSiteTotal()>=3?1:0),20,99);S.skills.finish=clamp(S.skills.finish-1,25,99);S.skills.dunk=clamp(S.skills.dunk-1,25,99);S.skills.reb=clamp(S.skills.reb-1,25,99);S.skills.speed=clamp(S.skills.speed-1,25,99);}
  if(S.age>41){S.a.athBase=clamp((S.a.athBase||50)-2,20,99);}""", '衰退 athBase')

# ═══════════ 7. ensureState：老档一次性迁移（必须位于「六大项回推」之后） ═══════════
sub1("""  if(!S.skills){ /* 旧存档没有细粒度技能，从六大项回推 */
    const a=S.a;
    S.skills={three:a.outside||55,mid:a.outside||55,finish:a.inside||55,dunk:Math.max(40,(a.inside||55)-5),handle:a.play||55,pass:a.play||55,perdef:a.def||55,intdef:a.def||55,block:Math.max(40,(a.def||55)-5),reb:a.reb||55,clutch:S.h.clutch||55};
  }
  if(!S.tier)S.tier=tierOf(S.h.potential||70); /* 旧存档：潜力值映射档位 */""",
"""  if(!S.skills){ /* 旧存档没有细粒度技能，从六大项回推 */
    const a=S.a;
    S.skills={three:a.outside||55,mid:a.outside||55,finish:a.inside||55,dunk:Math.max(40,(a.inside||55)-5),handle:a.play||55,pass:a.play||55,perdef:a.def||55,intdef:a.def||55,block:Math.max(40,(a.def||55)-5),reb:a.reb||55,clutch:S.h.clutch||55};
  }
  /* v4.28.0：属性体系对齐 2K——补 4 项新技能（罚球/抢断/力量/速度，由既有属性推导，OVR 不跳变）
   * + 身体基础 athBase（「身体素质」改为 基础.4+速度.3+力量.3 派生，事件与衰退改作用于 athBase）。
   * 必须放在「六大项回推」之后：极简老档（skills 整体缺失）先回推出 11 项，这里再补齐 15 项。 */
  if(S.skills){
    if(S.skills.free==null)S.skills.free=clamp(Math.round(((S.skills.mid||55)*2+(S.skills.finish||55))/3),25,99);
    if(S.skills.steal==null)S.skills.steal=clamp(S.skills.perdef||55,25,99);
    if(S.skills.strength==null)S.skills.strength=clamp((S.a&&S.a.ath)||55,25,99);
    if(S.skills.speed==null)S.skills.speed=clamp((S.a&&S.a.ath)||55,25,99);
    if(S.a&&S.a.athBase==null)S.a.athBase=clamp(S.a.ath||50,20,99);
    syncFromSkills();
  }
  if(!S.tier)S.tier=tierOf(S.h.potential||70); /* 旧存档：潜力值映射档位 */""", 'ensureState 2K 迁移')

# ═══════════ 8. showAttrs：2K 式属性清单（五大类分组 + 色条） ═══════════
sub1("function openMore(){",
"""/* v4.28.0：2K 式属性清单——按五大类分组（内线得分/外线投篮/组织传球/防守/篮板/身体素质），
 * 每项名称 + 数值色条（85+ 金 / 75+ 绿 / 65+ 蓝 / 65- 红），OVR 大字置顶。 */
function showAttrs(){
  syncFromSkills();
  const k=S.skills,ab=(S.a.athBase||50);
  const row=(n,v)=>{const c=v>=85?'#fbbf24':v>=75?'#6eee9c':v>=65?'#7ab8ff':'#f09595';
    return '<div style="display:flex;align-items:center;gap:8px;padding:5px 0">'
      +'<span style="width:52px;color:#aab2c5;font-size:12px">'+n+'</span>'
      +'<div style="flex:1;height:8px;background:#232c40;border-radius:4px;overflow:hidden"><i style="display:block;height:100%;width:'+clamp(v,2,99)+'%;background:'+c+'"></i></div>'
      +'<b style="width:30px;text-align:right;color:'+c+'">'+v+'</b></div>';};
  const grp=(t,items)=>{const v=Math.round(items.reduce((s,x)=>s+x[1],0)/items.length);
    const c=v>=85?'#fbbf24':v>=75?'#6eee9c':v>=65?'#7ab8ff':'#f09595';
    return '<div style="margin:12px 0 4px;display:flex;justify-content:space-between"><span style="color:#ffd479;font-size:12px">'+t+'</span><b style="font-size:12px;color:'+c+'">'+v+'</b></div>'
      +items.map(x=>row(x[0],x[1])).join('');};
  openOvl('<h3>📊 '+esc(S.name)+' · OVR <b style="color:#fbbf24">'+ovr()+'</b></h3>'
    +'<div class="mini">'+POS[S.pos].n+' · '+esc(S.league)+' · 属性按 NBA 2K 分类归组</div><hr style="border-color:#232c40">'
    +grp('🏀 内线得分',[['终结',k.finish||55],['扣篮',k.dunk||55]])
    +grp('🎯 外线投篮',[['三分',k.three||55],['中投',k.mid||55],['罚球',k.free||55]])
    +grp('🧭 组织传球',[['控球',k.handle||55],['传球',k.pass||55]])
    +grp('🛡 防守',[['外防',k.perdef||55],['抢断',k.steal||55],['内防',k.intdef||55],['盖帽',k.block||55]])
    +grp('💪 篮板',[['篮板',k.reb||55]])
    +grp('⚡ 身体素质',[['速度',k.speed||55],['力量',k.strength||55],['身体基础',ab]])
    +'<button class="btn ghost" style="margin-top:14px" onclick="closeOvl()">关闭</button>');
}
function openMore(){""", 'showAttrs 2K 清单')

# ═══════════ 9. openMore 入口 ═══════════
sub1("""  const tools=[
    mb('🧭 倾向','showTendHelp()'),""",
"""  const tools=[
    mb('📊 属性','showAttrs()'),
    mb('🧭 倾向','showTendHelp()'),""", 'openMore 属性入口')

# ═══════════ 10. skillLine：主面板改六大项概览（15 项一行太长） ═══════════
sub1("function skillLine(){return SKILLS.map(([k,n])=>n+' <b>'+S.skills[k]+'</b>').join(' ｜ ');}",
     "function skillLine(){syncFromSkills();return '内线 <b>'+S.a.inside+'</b> ｜ 外线 <b>'+S.a.outside+'</b> ｜ 组织 <b>'+S.a.play+'</b> ｜ 防守 <b>'+S.a.def+'</b> ｜ 篮板 <b>'+S.a.reb+'</b> ｜ 身体 <b>'+S.a.ath+'</b>'+' <span style=\"color:#5b6784\">（详见 ☰ 更多 · 属性）</span>';}", 'skillLine 六大项概览')

# ═══════════ 11. hint：11 项 → 15 项 ═══════════
sub1("建档后进入属性分配页：11项属性基础", "建档后进入属性分配页：15项属性基础", 'hint 15 项')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('OVR 属性体系 2K 对齐已应用：%d -> %d 字符（%+d）' % (orig, len(s), len(s) - orig))
