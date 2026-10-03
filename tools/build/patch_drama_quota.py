# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 9：戏剧配额防饿死（M1/P2 节奏复核的调参产物）

M1 模拟（30 生涯 / 1067 赛季）实测戏剧占比只有 24.7%，达不到 ≥30% 的验收线。
根因不是 EV_DRAMA_SHARE 不够高，而是两个机制的互锁：

  pickGeneric() 先按「本季题材不重复」过滤出 freshTopic，再在剩下的池子里
  按戏剧配额加权（缺戏时戏剧 9:1）。而戏剧事件高度集中在 trade / injury /
  nation 这几个题材上——这几个题材一被本季其他事件用掉，freshTopic 里的
  戏剧候选就清零，9:1 的加权只能作用在一堆流水账上，配额永远喂不饱。

  （代码注释自己写着「宁可撞题材，也别撞故事」，但实现把题材过滤放在了
   配额前面——正好把这句话反过来了。四季池的戏剧密度本来就不高
   （春 15% / 夏 25% / 秋 17% / 冬 18%），再被题材过滤器削一刀，
   实测就只剩 ~25%。）

修法：配额落后（need>0）且「题材未重复」的候选里已经没有戏剧时，
  允许戏剧事件从 freshAll（4 年内没讲过的全部候选）里撞题材出场。
  其余情况行为完全不变。调整前后数据见 build/sim_pacing.js + analyze_pacing.js。
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


# ═══════════ pickGeneric：戏剧配额不再被题材过滤器饿死 ═══════════
OLD = """  const freshAll=cand.filter(e=>!(S.recent[e.id]>year-EV_RECENT_YEARS));
  const freshTopic=freshAll.filter(e=>topics.indexOf(evTopicOf(e))<0);
  const finalPool=freshTopic.length?freshTopic:(freshAll.length?freshAll:cand);
  /* ③ 本季戏剧事件还不够时，给戏剧事件加权 */
  const need=Math.round((S.evSeen+1)*EV_DRAMA_SHARE)-S.evDrama;
  const weights=finalPool.map(e=>{"""
NEW = """  const freshAll=cand.filter(e=>!(S.recent[e.id]>year-EV_RECENT_YEARS));
  const freshTopic=freshAll.filter(e=>topics.indexOf(evTopicOf(e))<0);
  const need=Math.round((S.evSeen+1)*EV_DRAMA_SHARE)-S.evDrama;
  let finalPool=freshTopic.length?freshTopic:(freshAll.length?freshAll:cand);
  /* ③ 本季缺戏、而题材未重复的候选里已经没有戏剧时，允许戏剧事件撞题材出场。
   *    否则题材过滤器会把集中在 trade/injury 上的戏剧候选耗光，
   *    9:1 的加权只剩流水账可抽，45% 的配额实测只能跑到 ~25%。 */
  if(need>0&&!finalPool.some(e=>evKindOf(e)==='drama')){
    const da=freshAll.filter(e=>evKindOf(e)==='drama');
    if(da.length)finalPool=da;
  }
  const weights=finalPool.map(e=>{"""
s = sub1(OLD, NEW, 'pickGeneric 戏剧配额防饿死')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('戏剧配额防饿死已应用：%d -> %d 字符（%+d）' % (orig, len(s), len(s) - orig))
