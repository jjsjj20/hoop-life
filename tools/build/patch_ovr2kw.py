# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 43：OVR 公式改为 2K 式「技能直加权」（v4.29.0）

【背景】用户需求：「我想要改成2k的公式」。2K 的 OVR = 每个细分属性 × 该位置对该属性
  的权重（一级直接加权，权重按位置差异极大——中锋的内防/篮板/力量权重极高、三分几乎
  不算分；控卫反之）。现状是「15 项技能 → 合成六大项 → 六大项×位置权重」的两级近似。

【设计（用户确认：分布守恒 + 2K 式强差异）】
  新公式：OVR = Σ(技能 × SKILL_W[位置][技能])，SKILL_W 为 5 位置 × 15 属性权重表
  （clutch 保持隐藏属性语义不进 OVR；athBase 承载身体基础）。
  权重表由 _gen_skillw.py 生成：旧公式展开为「隐含权重」+ 手写 2K 位置特异偏好 δ，
  再对双约束（Σw=1 且 Σw×x0=旧公式典型 OVR）做最小二乘投影——
  ✓ 分布守恒：五位置典型画像新旧 OVR diff=0，三档画像漂移 ≤0.02
  ✓ 2K 式强差异：内线型 88 打 C=76/打 PG=66（跨位差 10）；后卫型 88 打 PG=75/打 C=62（差 13）
  ✓ 八处联动零重标（分布不变 → 薪资/门槛/奖项/难度 bump 全部沿用）

【改动】
  1. POS 表后新增 SKILL_W 常量（生成器输出）。
  2. ovr() 重写：直接技能加权（athBase 特判取 S.a.athBase；SKILL_W 缺失时回退旧公式防御）。
  3. ovrOf 保留六大项口径（仅用于选秀夜景快照显示，无 skills 对象的通用 OVR）。
  边界：六大项合成（syncFromSkills）保留——仍驱动 📊 属性/档案概览/事件奖励显示；
  GATED 门槛/薪资/难度 bump 不动（守恒）。
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


SKILL_W = """/* v4.29.0：2K 式 OVR 权重表——5 位置 × 15 属性直加权（clutch 保持隐藏属性不进 OVR）。
 * 由 _gen_skillw.py 生成：旧公式隐含权重 + 2K 位置特异偏好 δ，双约束（Σw=1 且
 * Σw×x0=旧公式典型 OVR）最小二乘投影——分布守恒（五位置典型画像 diff=0、
 * 三档画像漂移 ≤0.02）+ 2K 式强差异（内线型跨位差 10 / 后卫型跨位差 13）。 */
const SKILL_W={
  PG:{three:0.13838, mid:0.05617, free:0.03417, finish:0.04197, dunk:0.04966, handle:0.14805, pass:0.14805, perdef:0.03234, steal:0.03717, intdef:0.04623, block:0.05258, reb:0.0544, athBase:0.05712, speed:0.06343, strength:0.04029},
  SG:{three:0.13116, mid:0.0857, free:0.05363, finish:0.07686, dunk:0.05732, handle:0.1177, pass:0.07424, perdef:0.07166, steal:0.04252, intdef:0.04221, block:0.05081, reb:0.04086, athBase:0.06624, speed:0.05516, strength:0.03393},
  SF:{three:0.11453, mid:0.02974, free:0.03494, finish:0.09453, dunk:0.09494, handle:0.06494, pass:0.06056, perdef:0.07893, steal:0.06636, intdef:0.04857, block:0.04919, reb:0.10097, athBase:0.06174, speed:0.06332, strength:0.03675},
  PF:{three:0.04885, mid:0.04477, free:0.01434, finish:0.09131, dunk:0.10417, handle:0.0585, pass:0.0585, perdef:0.07104, steal:0.0645, intdef:0.06374, block:0.06747, reb:0.18774, athBase:0.05104, speed:0.02469, strength:0.04931},
  C:{three:0.04711, mid:0.02546, free:0.00963, finish:0.11051, dunk:0.10633, handle:0.04128, pass:0.04963, perdef:0.06548, steal:0.05728, intdef:0.06651, block:0.0515, reb:0.22818, athBase:0.05282, speed:0.04814, strength:0.04018}
};"""

# ═══════════ 1. SKILL_W 表（POS_ORDER 前） ═══════════
sub1("const POS_ORDER=['PG','SG','SF','PF','C'];", SKILL_W + "\nconst POS_ORDER=['PG','SG','SF','PF','C'];", 'SKILL_W 表')

# ═══════════ 2. ovr() 重写：技能直加权 ═══════════
sub1("function ovr(){if(!S)return 0;if(S.skills)syncFromSkills();let s=0;const w=POS[S.pos].w;COMPONENTS.forEach(k=>s+=(S.a[k]||0)*w[k]);return Math.round(s);}",
"""function ovr(){ /* v4.29.0：2K 式——15 项技能按位置直加权（SKILL_W），六大项仍合成供展示 */
  if(!S)return 0;
  if(S.skills)syncFromSkills();
  const W=SKILL_W[S.pos];
  if(!W){let s=0;COMPONENTS.forEach(k=>s+=(S.a[k]||0)*(POS[S.pos].w||{})[k]);return Math.round(s);}   /* 防御：无权重表回退旧公式 */
  let s=0;
  for(const k in W){
    const v=k==='athBase'?((S.a&&S.a.athBase)||55):((S.skills&&S.skills[k])||55);
    s+=v*W[k];
  }
  return Math.round(s);
}""", 'ovr 2K 直加权')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('OVR 2K 公式已应用：%d -> %d 字符（%+d）' % (orig, len(s), len(s) - orig))
