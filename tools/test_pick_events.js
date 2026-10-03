/* 签位主题事件 —— 脚手架见 ./testkit.js */
const path = require('path');
const { run } = require('./testkit');

module.exports = run('签位主题事件', ({ win, doc, check, errors, warns, html }) => {
  win.eval('renderCreate();');
  doc.querySelector('#fName').value = '测试';
  win.eval('doCreate(); allocRandom(); confirmAlloc();');

  const IDS = ['pk1', 'pk2', 'pk3', 'pk4'];
  const POOL_OF = { pk1: 'summer', pk2: 'summer', pk3: 'winter', pk4: 'autumn' };

  // ── 1. 注册情况 ────────────────────────────────────────
  const where = JSON.parse(win.eval(`JSON.stringify((function(){
    const o={};
    ['spring','summer','autumn','winter'].forEach(function(k){
      (POOLS[k]||[]).forEach(function(e){ o[e.id]=k; });
    });
    return o;
  })())`));
  IDS.forEach(id => check(`${id} 注册在 ${POOL_OF[id]} 池`, where[id] === POOL_OF[id], String(where[id])));
  check('pk2b 是剧情线第二段（不在事件池里）', !where.pk2b && !!win.eval('STORY.pk2b'));
  IDS.forEach(id => check(`${id} 被认定为戏剧事件`, win.eval(`EV_KIND_OVERRIDE.${id}`) === 'drama'));
  IDS.forEach(id => check(`${id} 设置了门槛`, typeof win.eval(`typeof GATED.${id}`) === 'string' && win.eval(`typeof GATED.${id}`) === 'function'));

  // ── 2. 职业门槛：职业球员能抽到、大学生抽不到 ───────────
  const gateAt = (lg, hi) => win.eval(`(function(){
    S.league=${JSON.stringify(lg)};
    const v=${hi?90:45};
    SKILLS.forEach(function(p){S.skills[p[0]]=v;});
    for(const k in S.a)S.a[k]=v;
    return {ovr:ovr(),pk1:GATED.pk1(),pk2:GATED.pk2(),pk3:GATED.pk3(),pk4:GATED.pk4()};
  })()`);
  const gNba = gateAt('NBA', true);
  check('NBA 高能力球员：四条都放行', gNba.pk1 && gNba.pk2 && gNba.pk3 && gNba.pk4,
    'ovr=' + gNba.ovr + ' ' + JSON.stringify(gNba));
  const gLow = gateAt('NBA', false);
  check('低能力球员：摆烂轮休事件被拦下（球队不在乎你）', gLow.pk3 === false, 'ovr=' + gLow.ovr);
  const gNcaa = gateAt('NCAA', true);
  check('NCAA 球员：四条都拦下（大学生没有球队选秀权）',
    !gNcaa.pk1 && !gNcaa.pk2 && !gNcaa.pk3 && !gNcaa.pk4, JSON.stringify(gNcaa));

  // ── 顺带修掉的季池 bug：职业线的 summer/autumn/winter 池以前根本抽不到 ──
  const pk = JSON.parse(win.eval(`JSON.stringify((function(){
    const out=[];
    ['spring','summer','autumn','winter'].forEach(function(st){
      S.stage=st;S.league='NBA';
      const k=poolKey();
      out.push({stage:st,key:k,own:(POOLS[k]||POOLS.spring)===POOLS[st],len:(POOLS[k]||[]).length});
    });
    S.league='青训';S.stage='summer';
    out.push({stage:'青训 summer',key:poolKey(),own:poolKey()==='youthSummer',len:(POOLS[poolKey()]||[]).length});
    return out;
  })())`));
  pk.forEach(r => check(`季池查找：${r.stage} → ${r.key} 命中本季池`,
    r.own && r.len > 5, r.key + ' len=' + r.len));
  // 修复前四个季节都会回退到同一个 spring 池（长度全等于 92）；
  // 现在四个池各自独立，长度不可能全相同。
  const lens = pk.slice(0, 4).map(r => r.len);
  check('四个职业季池相互独立（不再全部回退到 spring）',
    new Set(lens).size === 4, '长度 ' + lens.join(','));

  // ── 3. 内容可 materialize，且文本完整 ───────────────────
  win.eval("S.league='NBA';S.team='辽宁本钢';S.teamStr=7;");
  // 注意：池事件的 scene/title/o/fx 都是**函数**，JSON.stringify 会把函数丢掉，
  // 所以取数据必须整个放进页面里做，只把结果 stringify 出来。
  const mat = JSON.parse(win.eval(`JSON.stringify((function(){
    const out={};
    ['spring','summer','autumn','winter'].forEach(function(k){
      (POOLS[k]||[]).forEach(function(e){ if(['pk1','pk2','pk3','pk4'].indexOf(e.id)>=0) out[e.id]=materialize(e); });
    });
    out.pk2b=materialize(STORY.pk2b);
    return out;
  })())`));
  const meta = JSON.parse(win.eval(`JSON.stringify((function(){
    const out={};
    const grab=function(id,e){ out[id]={next:(e.choices||[]).map(function(c){return c.next||null;}),
      fx:(e.choices||[]).map(function(c){return typeof c.fx==='function'?c.fx():(c.fx||{});}),
      topic:evTopicOf(e)}; };
    ['spring','summer','autumn','winter'].forEach(function(k){
      (POOLS[k]||[]).forEach(function(e){ if(['pk1','pk2','pk3','pk4'].indexOf(e.id)>=0) grab(e.id,e); });
    });
    grab('pk2b',STORY.pk2b);
    return out;
  })())`));

  const ids = Object.keys(mat);
  ids.forEach(id => {
    const e = mat[id];
    check(`${id} 标题/正文/选项都是真文本`,
      typeof e.title === 'string' && e.title.length > 4 &&
      typeof e.scene === 'string' && e.scene.length > 30 &&
      Array.isArray(e.choices) && e.choices.length >= 3 &&
      e.choices.every(c => typeof c.t === 'string' && c.t.length > 2 && typeof c.o === 'string' && c.o.length > 6),
      id + ': ' + (e.choices || []).length + ' 个选项');
    check(`${id} 正文里带了球队名（动态求值生效）`, /辽宁本钢/.test(e.scene || ''), String(e.scene).slice(0, 40));
    check(`${id} 正文分了段落（用 \\n\\n 分段）`, (e.scene || '').indexOf('\n\n') >= 0);
  });

  // ── 4. fx 键全部已注册（未注册的键只会 console.warn，等于选项没效果）──
  const valid = JSON.parse(win.eval('JSON.stringify(FX.map(p=>p[0]))'));
  const badKeys = [];
  Object.keys(meta).forEach(id => {
    (meta[id].fx || []).forEach((fx, i) => {
      Object.keys(fx).forEach(k => { if (valid.indexOf(k) < 0) badKeys.push(id + '#' + i + ':' + k); });
    });
  });
  check('所有 fx 键都已在 FX 注册表里', badKeys.length === 0, badKeys.join(', '));

  // 真跑一遍 applyFx，确认控制台没有「未注册的效果键」告警
  warns.length = 0;
  win.eval(`(function(){
    ['pk1','pk2','pk3','pk4','pk2b'].forEach(function(id){
      const e=(STORY[id])?materialize(STORY[id]):null;
    });
    const all=[];
    ['spring','summer','autumn','winter'].forEach(function(k){(POOLS[k]||[]).forEach(function(x){all.push(x);});});
    all.concat(Object.keys(STORY).map(function(k){return STORY[k];})).forEach(function(e){
      (e.choices||[]).forEach(function(c){ applyFx(typeof c.fx==='function'?c.fx():(c.fx||{})); });
    });
  })();`);
  const fxWarns = warns.filter(w => /未注册的效果键/.test(w));
  check('全量 applyFx 无「未注册的效果键」告警', fxWarns.length === 0, fxWarns.slice(0, 3).join(' | '));

  // ── 5. 剧情线跳转 ──────────────────────────────────────
  check('pk2 的三个选项都指向 pk2b', meta.pk2.next.every(x => x === 'pk2b'), meta.pk2.next.join(','));
  const nextEv = JSON.parse(win.eval("JSON.stringify(evById('pk2b'))"));
  check('pk2b 能按 id 取到且可用', nextEv && nextEv.id === 'pk2b' && nextEv.choices.length === 3 && nextEv.scene.length > 30);

  // ── 6. 题材归类（影响同赛季题材去重）──────────────────
  check('pk1 归入「交易」题材', meta.pk1.topic === 'trade', meta.pk1.topic);
  check('pk2 归入「球队」题材', meta.pk2.topic === 'team', meta.pk2.topic);
  check('pk4 归入「球队」题材', meta.pk4.topic === 'team', meta.pk4.topic);

  // ── 7. 真的能被抽到 ────────────────────────────────────
  const draw = (stage, n) => JSON.parse(win.eval(`JSON.stringify((function(){
    S.league='NBA';S.stage=${JSON.stringify(stage)};
    const c={};
    for(let i=0;i<${n};i++){
      S.used={};S.usedTopics=[];S.recent={};   /* 每轮当作新赛季，从整池里抽 */
      const e=pickGeneric();
      c[e.id]=(c[e.id]||0)+1;
    }
    return c;
  })())`));
  const dSum = draw('summer', 600), dWin = draw('winter', 600), dAut = draw('autumn', 600);
  check('夏季池里能抽到 pk1', (dSum.pk1 || 0) > 0, '600 次里 ' + (dSum.pk1 || 0) + ' 次');
  check('夏季池里能抽到 pk2', (dSum.pk2 || 0) > 0, '600 次里 ' + (dSum.pk2 || 0) + ' 次');
  check('冬季池里能抽到 pk3', (dWin.pk3 || 0) > 0, '600 次里 ' + (dWin.pk3 || 0) + ' 次');
  check('秋季池里能抽到 pk4', (dAut.pk4 || 0) > 0, '600 次里 ' + (dAut.pk4 || 0) + ' 次');

  // 夏季池真的在用（不再全都回退到 spring 的 s*/sd* 事件）
  const springIds = win.eval('POOLS.spring.map(e=>e.id).join()');
  const summerOnly = win.eval(`POOLS.summer.filter(function(e){return ${JSON.stringify(springIds)}.split(',').indexOf(e.id)<0;}).length`);
  const gotSummerOnly = Object.keys(dSum).filter(id => springIds.split(',').indexOf(id) < 0).length;
  check('夏季抽到的事件里有春季池没有的（确认池子没回退）',
    summerOnly > 80 && gotSummerOnly > 10, '夏季独有 ' + summerOnly + ' 条，抽中 ' + gotSummerOnly + ' 条');

  check('抽到的 pk2 带 next=pk2b', win.eval(`(function(){
    S.league='NBA';S.stage='summer';
    for(let i=0;i<800;i++){S.used={};S.usedTopics=[];S.recent={};const e=pickGeneric();if(e.id==='pk2')return String(e.choices[0].next);}
    return 'none';
  })()`) === 'pk2b');

  // ── 结果 ───────────────────────────────────────────────
}, { ready: 1200 });
