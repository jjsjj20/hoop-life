# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 7：新增 5 条「球队签位」主题事件

设计取舍：
  · 只写「球员视角能真实撞上」的签位事件——管理层梭哈首轮签、球队选了同位置新秀、
    摆烂年让你轮休、更衣室开始算明年的顺位。球队间的签位交易细节玩家感知不到，不写。
  · 避开已有的同类事件：`sud2`（夏 · 被摆上货架）已经写过"球员进交易讨论"，
    所以不重复写"你被摆上货架"。
  · 全部用 isPro() 设门槛——青训走 youth 池本来就抽不到，但 NCAA 走的是同一批池子，
    不加门槛会让大学生撞上"球队用首轮签换了老将"。
  · 题材分类靠标题关键词（EV_TOPICS），标题里带上「交易 / 新秀 / 管理层 / 更衣室」，
    让它们在赛季内题材去重里各归各位。
"""
import os, re

BASE = os.path.dirname(os.path.abspath(__file__))
HTML = os.environ.get('GAME_HTML') or os.path.join(BASE, '..', 'output', '篮球人生.html')

s = open(HTML, encoding='utf-8').read()
orig = len(s)


def sub1(old, new, why):
    n = s.count(old)
    if n != 1:
        raise SystemExit('!! %s 匹配 %d 次' % (why, n))
    return s.replace(old, new)


# 先确认 id 没有撞车
for i in ['pk1', 'pk2', 'pk2b', 'pk3', 'pk4']:
    if re.search(r"evt\('%s'" % i, s) or re.search(r"story\('%s'" % i, s):
        raise SystemExit('id 冲突：%s 已存在' % i)


# ═══════════ 事件正文 ═══════════
PK1 = """
  /* ── 签位主题（新）─────────────────────────────────────────────
   * 球员视角能撞上的"签位"：管理层梭哈首轮签、球队选了同位置新秀、
   * 摆烂年让你轮休、更衣室开始算明年的顺位。 */
  evt('pk1','夏 · 首轮签在交易里送走了',()=>`选秀夜进行到一半，手机先响了——不是联盟的电话，是${S.team}官宣：今年的首轮签被打包送走，换回来一名 31 岁的即战力。

更衣室群里瞬间刷了几十条。有人发了个「终于想赢球了」的表情，也有人一句话没说，只发了个句号。

总经理单独给${S.name}发了条消息：「今年，我们想赢。」`,[
    ch('在群里表态：今年就要赢',{ts:1,stability:1},'他敲下那行字，几个老将跟着点了赞。这个赛季的目标，一下子统一了。'),
    ch('私下找总经理问清楚规划',{play:1,ts:1},'总经理把未来三年的账摊开讲了一遍。他听懂了球队的赌注——也听懂了赌注里有自己。'),
    ch('在采访里公开质疑这笔交易',{clutch:2,ts:-2,valuePct:.03},'那句话上了热搜。球迷站他这边，管理层沉默。此后三个月，他的名字一直挂在流言里。')
  ]),
  evt('pk2','夏 · 选秀夜，球队选中一名同位置新秀',()=>`选秀夜，${S.team}用手里的高顺位签，选中了一名和${S.name}打同一个位置的年轻人。镜头切到他脸上时，他正笑得很灿烂。

总经理发来的消息很短：「他会跟着你学。」

训练馆的储物柜，明天就要重排了。`,[
    nx(ch('主动带他，该教的都教',{ts:2,mate:2},'他把两年的训练笔记拍照发过去。新人回了一句：谢谢哥。更衣室都看在眼里。'),'pk2b'),
    nx(ch('把话挑明：位置是我的',{clutch:2,ts:-1},'他没有绕弯子。新人愣了两秒，点了点头。从此对抗训练里，两个人一次都没让过。'),'pk2b'),
    nx(ch('让经纪人去打听别的球队',{stability:-1,valuePct:.02},'经纪人打了六个电话。三家球队有兴趣，都还没到报价的程度。他第一次认真想了想"离开"这两个字。'),'pk2b')
  ]),
"""

PK3 = """
  /* ── 签位主题（新）：摆烂年，球队想让你"休息" ── */
  evt('pk3','冬 · 管理层希望我「休息」',()=>`赛季过半，${S.team}的战绩卡在一个微妙的位置——赢了没什么意义，输了反而更好。

总经理请${S.name}喝了杯咖啡，话说得很客气：「接下来这段时间，我们希望大家都健健康康的。」

队医办公室的门，忽然变得很好进。`,[
    ch('配合轮休，把身体养好',{durability:2,stability:1},'他歇了六场。身体前所未有地松快，可他总觉得那六场里少了点什么。'),
    ch('直接问教练：我们是想赢还是想选人',{clutch:2,play:1,ts:-1},'教练沉默了很久，说：你打你的。那之后他的上场时间不降，反而涨了。'),
    ch('照常出战，一场不落',{hustle:2,durability:-1,ts:1},'他在一支不想赢球的球队里，打出了职业生涯最完整的二十场。球迷都看见了。')
  ]),
"""

PK4 = """
  /* ── 签位主题（新）：更衣室开始算明年的顺位 ── */
  evt('pk4','秋 · 更衣室里在算明年的签位',()=>`又一次客场失利之后，${S.team}的大巴上没有放比赛录像。

后排有人小声说：「照这个输法，明年我们能抽到第几？」另一个声音接上来：「听说那个高中生，比今年的状元还猛。」

车厢里安静了两秒，然后有人笑了。

${S.name}坐在窗边，戴着耳机，其实什么也没在听。`,[
    ch('摘下耳机，把话头掐断',{ts:2,clutch:1},'「先把下一场打完再说。」车厢安静下来。这句话，教练在赛后原样复述给了记者。'),
    ch('和他们一起聊两句',{stability:1,mate:1},'他笑着接了一句。气氛松了，但他自己知道，那口气也跟着松了。'),
    ch('找教练谈球队的方向',{play:1,ts:1},'两个人聊了两个小时。教练说：这支球队缺的不是天赋，是还有人愿意当真。')
  ]),
"""

PK2B = """
/* 签位主题 · 剧情线后续：新秀在训练营把你打爆了（只在跳转时出现，不进事件池） */
story('pk2b','秋 · 新秀把你打爆了',()=>`${S.team}训练营第三周，全场对抗。那个新人在${S.name}头上投进第五个球的时候，替补席有人吹了声口哨。

教练把战术板合上，什么也没说。

晚饭时助教发来一段剪辑：全是这场对抗里他被过的回合。`,[
  ch('加练到凌晨，找回对抗的手感',{ath:1,clutch:1,hustle:1},'球馆的灯凌晨两点才关。第二天早饭时，他拿筷子的手在抖。'),
  ch('找教练调整，改打无球',{play:1,outside:1},'他不再每个回合都要球。球队的进攻反倒顺了，助攻数连着六场是正的。'),
  ch('把位置让给他，自己带第二阵容',{ts:2,mate:2,stability:1,starter:false},'第二阵容打出了全联盟最好的净胜分。他说：年轻人该上场，我该赢球。')
]);
"""

# ═══════════ 插入各季池 ═══════════
def append_to_pool(text, pool, block, why):
    """把事件块追加到某个池数组的结尾（在它的 \\n]; 之前）。
    注意：池里最后一条事件后面没有逗号，插进去之前要自己补一个。"""
    a = text.index('const %s=[' % pool)
    b = text.index('\n];', a)
    head = text[:b].rstrip()
    sep = '' if head.endswith(',') else ','
    return head + sep + '\n' + block.strip('\n') + '\n' + text[b:]


s = append_to_pool(s, 'SUMMER_POOL', PK1, 'pc1/pc2 进夏季池')
s = append_to_pool(s, 'WINTER_POOL', PK3, 'pk3 进冬季池')
s = append_to_pool(s, 'AUTUMN_POOL', PK4, 'pk4 进秋季池')

# 剧情线后续：放在池注册之前
s = sub1('POOLS.youthSpring=Y_SPRING;',
         PK2B.strip('\n') + '\n\nPOOLS.youthSpring=Y_SPRING;',
         '插入 pk2b 剧情线')

# ═══════════ 顺带修掉一个让 292 条事件变死代码的 bug ═══════════
# poolKey() 给非青训球员拼出的是 'Summer'（首字母大写），
# 而池子的注册名是全小写（POOLS.summer）——POOLS[key] 永远 undefined，
# 于是静默回退到 POOLS.spring：职业线只抽春季池，夏/秋/冬三池（292 条事件）从没被抽到过。
# 青训侧因为注册名本来就是 youthSpring/camelCase，反而正好对上。
s = sub1(
    "function poolKey(){return (S.league==='青训'?'youth':'')+(STAGE_KEY[S.stage]||'Spring');}",
    """function poolKey(){
  /* 池子注册名两套写法：青训是 camelCase（youthSpring），职业池是全小写（spring/summer/autumn/winter）。
   * 这里曾经统一按 STAGE_KEY 首字母大写去拼，结果职业线拼出 'Summer' 找不到池子、
   * 静默回退到 spring——夏/秋/冬三个池子（292 条事件）从来没被抽到过。
   * 青训侧因为键名本来就是 camelCase，反而正好对上，所以这个 bug 一直藏在职业线里。 */
  const st=S.stage;
  if(S.league==='青训')return 'youth'+(STAGE_KEY[st]||'Spring');
  return STAGE_KEY[st]?st:'spring';
}""",
    '修复季池查找：职业线的 summer/autumn/winter 池从未生效')

# ═══════════ 门槛与题材认定 ═══════════
s = sub1("""  w46:()=>{const st=S.h.stability||60;return st<72;}  /* 手感冰点：只有进攻不稳定的人才会遇上 */""",
         """  w46:()=>{const st=S.h.stability||60;return st<72;},  /* 手感冰点：只有进攻不稳定的人才会遇上 */
  /* 签位主题：只有职业球队才有选秀权。青训走 youth 池本来就抽不到，
   * 但 NCAA 走的是同一批池子，不加这道门会让大学生撞上"球队用首轮签换了老将"。 */
  pk1:()=>isPro(),
  pk2:()=>isPro(),
  pk3:()=>isPro()&&ovr()>=68,   /* 摆烂年让谁休息：得是球队真在乎的人 */
  pk4:()=>isPro()""",
         'GATED 加签位事件门槛')

s = sub1("""  st_bench2:'drama',st_trade2:'drama',st_feud2:'drama',st_lock2:'drama',st_deal2:'drama',st_stay2:'drama'
};""",
         """  st_bench2:'drama',st_trade2:'drama',st_feud2:'drama',st_lock2:'drama',st_deal2:'drama',st_stay2:'drama',
  pk1:'drama',pk2:'drama',pk3:'drama',pk4:'drama'   /* 签位主题：手工认定为戏剧 */
};""",
         'EV_KIND_OVERRIDE 加签位事件')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('签位主题事件已加入：%d -> %d 字符（+%d）' % (orig, len(s), len(s) - orig))
