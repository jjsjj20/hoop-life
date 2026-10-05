# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 23：难度重做（v4.20.0）

游玩反馈第五条：「难度太低，随便玩都可以成篮球之神」。30 生涯基线实测：
  峰值 OVR 均值 90.4（21/30 ≥90、12/30 ≥93）· 荣誉均值 125 项（多数生涯每季大满贯）
  · 生涯长度失控（41 岁终章后续战无上限，实测出现 55/64/69/70 岁、51 季）

三个根因与对应修复：
  ① 玩家成长上限过高：TIER_RANGE 整体下调（S 85-99 → 82-93）+
     GROWTH 收敛 16%→11%、训练加成 8→6、超限回落 92/82 → 90/76；
  ② 联盟没有真对手：NPC 能力 R.int(55,88) → R.int(54,92)、潜力上限 96→97
     （之前玩家 95+ 无人能争 → MVP/得分王/冠军每季大满贯）；
  ③ 「继续征战」只写了一个从未被读取的 flag：现在真的延长生涯（每次 +1 年、
     最多 3 次），45 岁开局强制退役——生涯最长到 45 岁。
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


# ═══════════ 1. 天赋上限整体下调 ═══════════
sub1("const TIER_RANGE={S:{min:85,max:99},A:{min:70,max:84},B:{min:65,max:75},C:{min:45,max:75},D:{min:35,max:70}};",
"""/* v4.20.0 难度重做：天赋上限整体下调——S 档不再是「随便玩都能满级」的通行证 */
const TIER_RANGE={S:{min:82,max:93},A:{min:68,max:82},B:{min:62,max:74},C:{min:45,max:70},D:{min:35,max:60}};""", 'TIER_RANGE 下调')

# ═══════════ 2. 成长曲线：到顶更慢、训练加成更少、成年回落更快 ═══════════
sub1("""  convUp:.16,         /* 向上限自然收敛比例（原 .30） */
  overKeepYouth:.92,  /* ≤24 岁：超出上限的部分每年保留 92% */
  overKeep:.82,       /* ≥25 岁：超出部分每年保留 82% */
  grindPerAlloc:.8,   /* 初始分配：每点「超出基准」的分配折算成长值 */
  grindMax:8,         /* 训练最多把上限抬高几点 */""",
"""  convUp:.11,         /* v4.20.0：向上限收敛 16%→11%——到顶更慢，光靠天赋不够 */
  overKeepYouth:.90,  /* ≤24 岁：超出上限的部分每年保留 90% */
  overKeep:.76,       /* ≥25 岁：超出部分每年保留 76%（成年后加练红利回落更快） */
  grindPerAlloc:.8,   /* 初始分配：每点「超出基准」的分配折算成长值 */
  grindMax:6,         /* v4.20.0：训练最多把上限抬高 6 点（原 8） */""", 'GROWTH 曲线')

# ═══════════ 3. NPC 强度：联盟要有真对手 ═══════════
sub1("  const o=R.int(55,88);",
     "  const o=R.int(54,92);   /* v4.20.0：联盟顶星上限 88→92——让 MVP/得分王真有对手 */", 'NPC 能力上限')
sub1("    pot:clamp(o+room,o,96)};", "    pot:clamp(o+room,o,97)};", 'NPC 潜力上限')

# ═══════════ 4. 继续征战：真的续战（+1 年），最多 3 次 ═══════════
sub1("""  ['continued',()=>{}],    /* 继续征战（41岁终章）：advance() 中处理 */""",
"""  /* v4.20.0：继续征战 = 真的再打一年（最多 3 次，45 岁开局强制退役） */
  ['continued',(v,c)=>{
    S.flags.contN=(S.flags.contN||0)+1;
    c.push('💪 续战第 '+S.flags.contN+' 年——他决定再打一年');
    S.log.push({y:seasonLabel(),t:'宣布再战一年（第'+S.flags.contN+'次）'});}],""", '续战 FX')

# ═══════════ 5. 终章：41 岁起每年冬再问一次，续满 3 次后不再询问 ═══════════
sub1("""  [()=>S.age===41&&S.stage==='winter'&&!S.flags.final,()=>{S.flags.final=true;return evFinal();}],""",
"""  /* v4.20.0：终章可续战——41 岁起每年冬问一次，直到续满 3 次（或退役） */
  [()=>S.age>=41&&S.stage==='winter'&&(S.flags.contN||0)<3&&S.flags.finalY!==S.age,
    ()=>{S.flags.finalY=S.age;if(S.age===41)S.flags.final=true;return evFinal();}],""", '终章续战规则')

# ═══════════ 6. 45 岁开局强制退役（续战硬上限）═══════════
sub1("""function nextYear(){
  S.age++;""",
"""function nextYear(){
  /* v4.20.0：续战硬上限——45 岁开局强制退役（生涯最长打到 45 岁） */
  if(S.age>=45&&!S.retired){S.retired=true;UI={mode:'end'};save();showEnd();return;}
  S.age++;""", '强制退役')

# ═══════════ 7. 终章文案：年龄动态 ═══════════
sub1("""function evFinal(){return {id:'final',title:'冬 · 终章，41岁',scene:`${S.birthYear+S.age}年冬天，${S.name}迎来了41岁。""",
"""function evFinal(){return {id:'final',title:'冬 · 终章，'+S.age+'岁',scene:`${S.birthYear+S.age}年冬天，${S.name}迎来了${S.age}岁。""", '终章文案动态')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('难度重做已应用：%d -> %d 字符（%+d）' % (orig, len(s), len(s) - orig))
