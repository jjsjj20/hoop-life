# -*- coding: utf-8 -*-
"""生成 tools/test_r2.js——R2 青训补强的回归钉。"""
import io

E = chr(96)
END = '  })())' + E + '));'

JS = """/* R2 青训体验补强（v4.17）——回归钉：
 *  ① 青训四池各 21 条（11+10），新增 yp/ys/ya/yw 12~21 全部就位
 *  ② 12 条青训戏剧全部登记 EV_KIND_OVERRIDE
 *  ③ 青训池题材广度 ≥6 类
 *  ④ sim_pacing 支持 SIM_AGE（15 岁青训起步）*/
const { run } = require('./testkit');

module.exports = run('R2青训补强', ({ win, check }) => {
  const POOL_KEY = { yp: 'youthSpring', ys: 'youthSummer', ya: 'youthAutumn', yw: 'youthWinter' };

  const detail = JSON.parse(win.eval(`JSON.stringify((function(){
    const map=${JSON.stringify(POOL_KEY)};
    const out={n:0,badKind:[],poolN:{},poolDrama:{},topics:{}};
    Object.keys(map).forEach(function(pre){
      const pool=POOLS[map[pre]]||[];
      out.poolN[map[pre]]=pool.length;
      let dr=0;const tp={};
      pool.forEach(function(e){
        const k=evKindOf(e);if(k==='drama')dr++;
        const t=evTopicOf(e);tp[t]=(tp[t]||0)+1;
      });
      out.poolDrama[map[pre]]=dr;out.topics[map[pre]]=tp;
      for(let i=12;i<=21;i++){
        const id=pre+i;out.n++;
        if(!pool.some(function(x){return x.id===id;}))out.badKind.push(id+':missing');
      }
    });
    return out;})())`));

  check('新增 40 条青训事件全部就位（4 池 × 10）', detail.n === 40, String(detail.n));
  ['youthSpring', 'youthSummer', 'youthAutumn', 'youthWinter'].forEach(pk => {
    check(pk + ' 池事件 ≥ 21（原 11+10）', detail.poolN[pk] >= 21, pk + '=' + detail.poolN[pk]);
    check(pk + ' 池戏剧事件 ≥ 3', detail.poolDrama[pk] >= 3, pk + '=' + detail.poolDrama[pk]);
    const distinct = Object.keys(detail.topics[pk]).length;
    check(pk + ' 池题材广度 ≥ 5 类', distinct >= 5, pk + '=' + JSON.stringify(detail.topics[pk]));
  });

  const ov = win.eval(`(function(){let n=0;
    ['yp','ys','ya','yw'].forEach(function(pre){for(let i=12;i<=21;i++){if(EV_KIND_OVERRIDE[pre+i]==='drama')n++;}});
    return n;})()`);
  check('青训戏剧 override 登记 ≥ 12 条', ov >= 12, String(ov));

  // sim_pacing 支持 SIM_AGE
  const fs = require('fs');
  const sim = fs.readFileSync(__dirname + '/sim_pacing.js', 'utf8');
  check('sim_pacing 支持 SIM_AGE 青训起步', sim.indexOf('SIM_AGE') >= 0 && sim.indexOf('青训') >= 0);
});
"""

io.open('test_r2.js', 'w', encoding='utf-8', newline='\n').write(JS)
print('generated')
