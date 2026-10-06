# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 32：清掉行动栏残留的吸底「继续」（v4.21.1）

实机游玩（jsdom 驱动完整生涯一局）发现：结果页 v4.19.1 注入吸底行动栏的
「继续 ▶」(.contAct) 会残留到下一页——赛季总结/颁奖夜（finishSeason/awardsNext）
直接渲染 #stage、不重渲整页，行动栏不重建，上一个结果页注入的 .contAct 就
活着跟过来：移动端可见、点不动（advance 的模式守卫拦着，不会误推进，但玩家
会看到一个失灵的按钮）。桌面端 .contAct 被 CSS 隐藏，所以一直没被发现。

方案：加 clearContAct() 小助手，renderSeason / renderAwards 入口各调一次——
覆盖全部三条直接渲染路径（finishSeason→season、finishSeason→awards、
awardsNext→season）。showEnd 重绘整个 #app、nextYear 走 renderGame，
行动栏都会重建，均无此问题，不必处理。
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


# ═══════════ 1. helper + renderAwards 入口清理 ═══════════
sub1("""  kbHint();
}
function renderAwards(awards,res){
  const box=$('#stage');""",
"""  kbHint();
}
/* v4.21.1：清掉行动栏里残留的吸底「继续」——赛季总结/颁奖夜直接渲染 #stage、
 * 不重渲整页，上一个结果页注入的 .contAct 会活着跟过来：移动端可见、点不动
 * （advance 的模式守卫拦着不会误推进，但玩家会看到一个失灵的按钮）。 */
function clearContAct(){try{const _ca=document.querySelector('.actions .contAct');if(_ca)_ca.remove();}catch(e){}}
function renderAwards(awards,res){
  clearContAct();
  const box=$('#stage');""", 'helper + renderAwards 入口')

# ═══════════ 2. renderSeason 入口清理 ═══════════
sub1("""function renderSeason(res){
  const box=$('#stage');""",
"""function renderSeason(res){
  clearContAct();
  const box=$('#stage');""", 'renderSeason 入口')

open(HTML, 'w', encoding='utf-8', newline='').write(s)
print('行动栏残留「继续」清理已应用：%d -> %d 字符（%+d）' % (orig, len(s), len(s) - orig))
