# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 16：R3 摆烂机制实装（v4.16.0）

v4.14.0 的「管理层的暗示」此前只是叙事抉择——接受后战绩没有任何真实反馈。
本补丁把它变成机制：

  ① 摆烂抉择（默许轮换）写入 S.flags.tankYear（=当前生涯年）；
  ② computeStandings 对摆烂球队施加 **wpc −0.15**（15 个百分点，v4.21.2 由 10 上调；验收线 ≥5）——
     排名面板/选秀顺位/赛季总结全部同源生效；tankYear 只对当前赛季匹配，
     nextYear 之后自动过期（想再摆，得再谈一次）；
  ③ 接受摆烂时清空排名缓存（S._stCache），惩罚立即生效；
  ④ 赛季结算写入 tankNote，renderSeason 展示「📉 管理层按下了计时器」。

签位闭环：摆烂 → 我队槽位更差（战绩最差排最前）→ 落入保护区 →
选秀夜签位归还原队（v4.11 的触保机制自然兑现）。
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


# ═══════════ 1. FX 注册：tankAccept（默许摆烂）═══════════
sub1("""    S.log.push({y:seasonLabel(),t:'被交易至 '+to+'（换回签位资产）'});}],""",
"""    S.log.push({y:seasonLabel(),t:'被交易至 '+to+'（换回签位资产）'});}],
  /* R3（v4.16）：摆烂机制——默许摆烂后，本季我队胜率被压低（-15 个百分点，v4.21.2 上调），
   * 换来签位触保回退的可能；只在当前赛季生效，跨年自动过期。 */
  ['tankAccept',(v,c)=>{
    S.flags.tankYear=S.birthYear+S.age;
    S._stCache={};                        /* 排名缓存失效：惩罚立即生效 */
    c.push('📉 管理层按下了计时器——这一年的战绩，为未来签位让路');
    S.log.push({y:seasonLabel(),t:'默许摆烂：战绩为未来签位让路'});}],""", 'FX 注册 tankAccept')

# ═══════════ 2. computeStandings：摆烂惩罚 ═══════════
sub1("""    if(t[0]===myTeamName()){
      /* 玩家球队：波动收窄（实力决定命运），并按 OVR 加成 */
      const adj=ovr()-70;
      wpc=clamp(.38-lgHard(lg).wpc+(st-6.5)*.055+adj*.005+R.float(-.06,.06),.06,.95);
    }""",
"""    if(t[0]===myTeamName()){
      /* 玩家球队：波动收窄（实力决定命运），并按 OVR 加成；
       * R3（v4.16）：默许摆烂的赛季，胜率压低 15 个百分点（v4.21.2 由 10 上调；验收线 ≥5）——
       * 槽位更差 → 落入保护区 → 选秀夜签位触保回退（v4.11 机制自然兑现） */
      const tankPad=(S.flags.tankYear===(S.birthYear+S.age))?0.15:0;
      const adj=ovr()-70;
      wpc=clamp(.38-lgHard(lg).wpc+(st-6.5)*.055+adj*.005-tankPad+R.float(-.06,.06),.06,.95);
    }""", 'computeStandings 摆烂惩罚')

# ═══════════ 3. 赛季结算文案 ═══════════
sub1("""  codexSeason();              /* 图鉴：本队/联赛/队友/最强队友 */""",
"""  codexSeason();              /* 图鉴：本队/联赛/队友/最强队友 */
  /* R3（v4.16）：摆烂赛季的结算文案（renderSeason 展示） */
  if(S.flags.tankYear===(S.birthYear+S.age))res.tankNote='管理层按下了计时器——这一年的战绩，为未来签位让了路';""",
  '结算写入 tankNote')

# ═══════════ 4. renderSeason 展示 ═══════════
sub1("""  <div class="row"><span>战绩</span><b>${esc(res.record)}</b></div>
  <div class="row"><span>结果</span><b>${esc(res.playoffs)}</b></div>""",
"""  <div class="row"><span>战绩</span><b>${esc(res.record)}</b></div>
  ${res.tankNote?`<div class="row"><span>📉 摆烂</span><b style="color:#f87171">${esc(res.tankNote)}</b></div>`:''}
  <div class="row"><span>结果</span><b>${esc(res.playoffs)}</b></div>""", 'renderSeason 摆烂行')

# ═══════════ 5. evTankHint 默许选项挂上机制 ═══════════
sub1("""    ch('默许轮换：给年轻人让路',{stability:-2,ts:-1,hustle:1},'他开始打起了「养生篮球」。年轻人的上场时间涨了，他的数据落了。'),""",
"""    ch('默许轮换：给年轻人让路',{stability:-2,ts:-1,hustle:1,tankAccept:1},'他开始打起了「养生篮球」。年轻人的上场时间涨了，他的数据落了。'),""", '摆烂抉择挂 tankAccept')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('R3 摆烂机制已应用：%d -> %d 字符（%+d）' % (orig, len(s), len(s) - orig))
