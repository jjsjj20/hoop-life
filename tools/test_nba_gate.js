/* NBA 门槛——选秀行情（v4.27.2 班底曲线同尺）+ FMVP 公式验收：
 * ① 行情 = 班底曲线逆函数（确定性公式，逐值精确校验）
 * ② 旧档位已移除、新公式就位
 * ③ FMVP 新公式就位（NBA / CBA·欧洲），旧 35% 下限与固定 .45 已移除 */
const { run } = require('./testkit');

module.exports = run('NBA门槛', ({ win, check, html }) => {
  win.eval('renderCreate();');
  win.eval("document.getElementById('fName').value='门槛测试';");
  win.eval('doCreate(); allocRandom(); confirmAlloc();');
  win.eval("S.age=20; S.league='NBA'; S.stage='winter';");

  /* 与产物一致的行情公式（v4.27.2：58-(o-40)/0.55 + 年龄修正，无随机） */
  const expStock = (o, age) => Math.max(1, Math.min(72, Math.round(
    58 - (o - 40) / 0.55 + (age >= 23 ? 4 : age >= 22 ? 3 : age >= 21 ? 1 : 0) - (age <= 19 ? 1 : 0))));
  const boost = t => win.eval(`
    (function(to){let d=to-ovr();if(d>0){Object.keys(S.skills).forEach(k=>{S.skills[k]=Math.min(99,Math.round((S.skills[k]||60)+d));});}})(${t});
    S.age=20;
  `);

  for (const target of [58, 63, 67, 71, 75, 79, 84]) {
    boost(target);
    const res = JSON.parse(win.eval(`JSON.stringify((function(){
      S.age=20;const o=ovr();
      const s1=draftStockInit(),s2=draftStockInit();
      return {o:o,s1:s1,s2:s2};
    })())`));
    const exp = expStock(res.o, 20);
    check(`ovr ${res.o} 的行情 = 曲线期望（${exp}）`, res.s1 === exp, `实得 ${res.s1}`);
    check(`行情为确定性公式（两次一致）`, res.s1 === res.s2, `${res.s1} vs ${res.s2}`);
  }

  check('旧档位已移除（70 分档 33-55）', html.indexOf('base=R.float(33,55)') < 0);
  check('新公式就位（班底曲线逆函数 58-(o-40)/0.55）', html.indexOf('58-(o-40)/0.55') >= 0);

  check('NBA FMVP 新公式就位（去除 35% 下限）', html.indexOf('clamp(.05+(o-70)*.05+(top?.2:0),.05,.85)') >= 0);
  check('CBA/欧洲 FMVP 新公式就位', html.indexOf('clamp(.05+(o-70)*.05+(_board.my.mvp<=3?.15:0),.05,.85)') >= 0);
  check('旧 NBA FMVP 公式已移除', html.indexOf('clamp(.35+(o-78)*.05') < 0);
  check('旧 CBA FMVP 固定 .45 已移除', html.indexOf('_board.my.mvp<=6&&R.chance(.45)') < 0);
});
