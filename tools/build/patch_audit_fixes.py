# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 8：代码审查后修 bug + 清理

审查发现的问题（用 build/audit.js 的 AST 扫描 + 真机流程复现）：

★ 严重（v4.9.3 引入，尚未部署，属于自查发现）
  evDraftDeclare() 自己构造了 S.draft：
      S.draft={stock:draftStockInit(),order:nbaDraftOrder(),promise:null,pick:null,y:seasonLabel()}
  只带了 5 个字段，**漏了 draw / lotto / slot**。而 ensureDraft() 的重新生成条件是
  「order 缺失 或 长度不对 或 赛季变了」——都不成立，于是抽签数据永远补不上。
  后果：v4.9.3 加的「选秀夜播报乐透抽签结果」在真实流程里从不出现
  （之前的测试恰好绕开了这条路径，是直接调 evDraftNight() 触发的 ensureDraft()）。
  同一处还导致 doDraft() 里 changes.push(lottoText(...)) 推入空字符串。

★ 一般
  · nbaDraftOrder / cbaDraftOrder 在改用 draftOrderOf 之后成了死代码。
  · lottoText() 在 draw 缺失时返回 ''，调用方直接 push 会产生空条目。

修法：把「构造一届选秀」收敛成唯一工厂 newDraft()，两处都走它——
  以后再加字段不可能只补一半。
"""
import os

BASE = os.path.dirname(os.path.abspath(__file__))
HTML = os.environ.get('GAME_HTML') or os.path.join(BASE, '..', 'output', '篮球人生.html')

s = open(HTML, encoding='utf-8').read()
orig = len(s)


def sub1(old, new, why):
    n = s.count(old)
    if n != 1:
        raise SystemExit('!! %s 匹配 %d 次' % (why, n))
    return s.replace(old, new)


# ═══════════ 1. 收敛成唯一工厂 newDraft()，并去掉死代码 ═══════════
OLD = """function nbaDraftOrder(){return draftOrderOf('nba').order;}
function cbaDraftOrder(){return draftOrderOf('cba').order;}"""
NEW = """/* 一届选秀的唯一构造点。
 * 之前 evDraftDeclare() 和 ensureDraft() 各写各的对象字面量，结果申报那条路漏了
 * draw / lotto / slot，抽签播报永远出不来——而且不报错，只是内容悄悄少了。
 * 现在只留这一个工厂，加字段不可能只补一半。 */
function newDraft(){
  const m=draftOrderOf('nba');
  return {stock:draftStockInit(),order:m.order,draw:m.draw,lotto:m.lotto,slot:m.slot,
          promise:null,pick:null,y:seasonLabel()};
}"""
s = sub1(OLD, NEW, '签位生成收敛为唯一工厂')

# ═══════════ 2. ensureDraft 也负责补字段 ═══════════
OLD_ENSURE = """function ensureDraft(){
  if(!S.draft)S.draft={stock:draftStockInit(),order:null,draw:null,lotto:null,promise:null,pick:null,y:null};
  /* 签位按赛季重抽：旧实现一旦生成就永久复用，换一年还是同一张签位表 */
  if(!S.draft.order||S.draft.order.length!==TEAMS.nba.length||S.draft.y!==seasonLabel()){
    const m=draftOrderOf('nba');
    S.draft.order=m.order;S.draft.draw=m.draw;S.draft.lotto=m.lotto;S.draft.slot=m.slot;S.draft.y=seasonLabel();
  }
  if(typeof S.draft.stock!=='number'||!Number.isFinite(S.draft.stock))S.draft.stock=draftStockInit();
  return S.draft;
}"""
NEW_ENSURE = """function ensureDraft(){
  if(!S.draft)S.draft={stock:null,order:null,draw:null,lotto:null,slot:null,promise:null,pick:null,y:null};
  /* 签位按赛季重抽：旧实现一旦生成就永久复用，换一年还是同一张签位表。
   * 另外把 !S.draft.draw 也算进"不完整"——老存档 / 半途造出来的 draft 缺抽签数据时能自愈。 */
  if(!S.draft.order||S.draft.order.length!==TEAMS.nba.length||S.draft.y!==seasonLabel()||!S.draft.draw){
    const m=draftOrderOf('nba');
    S.draft.order=m.order;S.draft.draw=m.draw;S.draft.lotto=m.lotto;S.draft.slot=m.slot;S.draft.y=seasonLabel();
  }
  if(typeof S.draft.stock!=='number'||!Number.isFinite(S.draft.stock))S.draft.stock=draftStockInit();
  return S.draft;
}"""
s = sub1(OLD_ENSURE, NEW_ENSURE, 'ensureDraft 支持补字段自愈')

# ═══════════ 3. 申报流程改走工厂 ═══════════
OLD_DECLARE = """S.draft={stock:draftStockInit(),order:nbaDraftOrder(),promise:null,pick:null,y:seasonLabel()};"""
NEW_DECLARE = """S.draft=newDraft();   /* 唯一工厂：行情 + 签位 + 抽签数据一次给全 */"""
s = sub1(OLD_DECLARE, NEW_DECLARE, '申报流程改走 newDraft()')

# ═══════════ 4. 不要往 changes 里推空字符串 ═══════════
s = sub1("""    changes.push(lottoText(cm.draw,cm.slot));""",
         """    const _lt=lottoText(cm.draw,cm.slot);if(_lt)changes.push(_lt);""",
         'CBA 播报防空条目')
s = sub1("""  if(d.draw&&d.draw.length&&pick!==1)changes.push('🎯 '+lottoText(d.draw,d.slot));""",
         """  if(pick!==1){const _lt=lottoText(d.draw,d.slot);if(_lt)changes.push('🎯 '+_lt);}""",
         'NBA 播报防空条目')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('审查修复已应用：%d -> %d 字符（%+d）' % (orig, len(s), len(s) - orig))
