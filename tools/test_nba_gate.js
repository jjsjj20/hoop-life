/* NBA 门槛——选秀行情后移 + FMVP 公式验收（v4.23.0）：
 * ① 选秀行情每个评分段落在新档区间（真随机抽样 120 次验证边界）
 * ② 旧档位已移除、新档位就位
 * ③ FMVP 新公式就位（NBA / CBA·欧洲），旧 35% 下限与固定 .45 已移除 */
const { run } = require('./testkit');

module.exports = run('NBA门槛', ({ win, check, html }) => {
  win.eval('renderCreate();');
  win.eval("document.getElementById('fName').value='门槛测试';");
  win.eval('doCreate(); allocRandom(); confirmAlloc();');
  win.eval("S.age=20; S.league='NBA'; S.stage='winter';");

  /* 与产物一致的档位表（else 档 61-76 被 clamp(...,72) 收顶为 61-72） */
  const tierOf = o => {
    if (o >= 86) return [4, 12];
    if (o >= 82) return [9, 20];
    if (o >= 78) return [15, 28];
    if (o >= 74) return [24, 42];
    if (o >= 70) return [33, 55];
    if (o >= 67) return [43, 62];
    if (o >= 64) return [53, 70];
    return [61, 72];
  };
  const boost = t => win.eval(`
    (function(to){let d=to-ovr();if(d>0){Object.keys(S.skills).forEach(k=>{S.skills[k]=Math.min(99,Math.round((S.skills[k]||60)+d));});}})(${t});
    S.age=20;
  `);

  for (const target of [58, 63, 67, 71, 75, 79, 84]) {
    boost(target);
    const res = JSON.parse(win.eval(`JSON.stringify((function(){
      const arr=[];for(let i=0;i<120;i++){S.age=20;arr.push(draftStockInit());}
      return {o:ovr(),min:Math.min.apply(null,arr),max:Math.max.apply(null,arr)};
    })())`));
    const lo = tierOf(res.o)[0], hi = tierOf(res.o)[1];
    check(`ovr ${res.o} 的行情落在新档 [${lo},${hi}]`, res.min >= lo && res.max <= hi, `实得 ${res.min}-${res.max}`);
  }

  check('旧档位已移除（70 分档 28-44）', html.indexOf('base=R.float(28,44)') < 0);
  check('新档位就位（70 分档 33-55）', html.indexOf('base=R.float(33,55)') >= 0);
  check('新档位就位（67 分档 43-62）', html.indexOf('base=R.float(43,62)') >= 0);

  check('NBA FMVP 新公式就位（去除 35% 下限）', html.indexOf('clamp(.05+(o-70)*.05+(top?.2:0),.05,.85)') >= 0);
  check('CBA/欧洲 FMVP 新公式就位', html.indexOf('clamp(.05+(o-70)*.05+(_board.my.mvp<=3?.15:0),.05,.85)') >= 0);
  check('旧 NBA FMVP 公式已移除', html.indexOf('clamp(.35+(o-78)*.05') < 0);
  check('旧 CBA FMVP 固定 .45 已移除', html.indexOf('_board.my.mvp<=6&&R.chance(.45)') < 0);
});
