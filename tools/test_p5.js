/* P5 内容补给（v4.13）——验收钉：
 *  ① 四季职业池各 +12 条戏剧事件（sd/sud/ad/wd 9~20），全部手工登记为戏剧
 *  ② 新事件题材落在 life / health / market（补戏剧密度洼地）
 *  ③ 次轮签归属播报代码就位（NBA + CBA） */
const { run } = require('./testkit');

module.exports = run('P5内容', ({ win, check, html }) => {
  const NEW = { sd: 12, sud: 12, ad: 12, wd: 12 };   // 每池新增 12 条
  const POOL_KEY = { sd: 'spring', sud: 'summer', ad: 'autumn', wd: 'winter' };
  const TOPICS_OK = ['trade', 'injury', 'nation', 'team', 'media', 'market', 'train', 'life', 'health'];

  // 直接逐条检查
  const detail = JSON.parse(win.eval(`JSON.stringify((function(){
    const TOPICS9="trade,injury,nation,team,media,market,train,life,health".split(',');const map=${JSON.stringify(POOL_KEY)};
    const out={n:0,badKind:[],badTopic:[],poolDrama:{},poolN:{},topics:{}};
    Object.keys(map).forEach(function(pre){
      const pk=map[pre];const pool=POOLS[pk]||[];
      out.poolN[pk]=pool.length;
      let dr=0;const tp={};
      pool.forEach(function(e){
        const k=evKindOf(e);if(k==='drama')dr++;
        const t=evTopicOf(e);tp[t]=(tp[t]||0)+1;
      });
      out.poolDrama[pk]=dr;out.topics[pk]=tp;
      for(let i=9;i<=20;i++){
        const id=pre+i;out.n++;
        const e=pool.find(function(x){return x.id===id;});
        if(!e){out.badKind.push(id+':missing');return;}
        if(evKindOf(e)!=='drama')out.badKind.push(id+':'+evKindOf(e));
        const t=evTopicOf(e);
        if(TOPICS9.indexOf(t)<0)out.badTopic.push(id+':'+t);
      }
    });
    return out;})())`));

  check('新增 48 条事件全部就位（4 池 × 12）', detail.n === 48, String(detail.n));
  check('新事件全部被认定为戏剧（EV_KIND_OVERRIDE/关键词）', detail.badKind.length === 0, detail.badKind.join(','));
  check('新事件题材全部是合法题材（9 类之一）', detail.badTopic.length === 0, detail.badTopic.join(','));
  ['spring', 'summer', 'autumn', 'winter'].forEach(pk => {
    check(pk + ' 池戏剧事件 ≥ 26（原 14+ / 新 12）', (detail.poolDrama[pk] || 0) >= 26,
      pk + '=' + detail.poolDrama[pk]);
    const t = detail.topics[pk] || {};
    const distinct = Object.keys(t).length;
    check(pk + ' 池题材广度 ≥ 7 类（戏剧供给不再集中 trade/injury）', distinct >= 7, pk + '=' + JSON.stringify(t));
  });

  // override 完整性：48 个新 id 都在 EV_KIND_OVERRIDE 里
  const ov = win.eval(`(function(){let n=0;
    ['sd','sud','ad','wd'].forEach(function(pre){for(let i=9;i<=20;i++){if(EV_KIND_OVERRIDE[pre+i]==='drama')n++;}});
    return n;})()`);
  check('EV_KIND_OVERRIDE 登记 48 条新 id', ov === 48, String(ov));

  // 次轮归属播报（NBA + CBA）
  check('NBA 次轮归属播报代码就位', html.indexOf("else if(!r1&&team!==slotTeam)changes.push('📋 次轮该签原属 '") >= 0);
  check('CBA 次轮归属播报代码就位', html.indexOf("else if(!cbaR1&&team!==slotTeam)changes.push('📋 次轮该签原属 '") >= 0);

  // 池大小：4 职业池各 +12（442 → 490 池事件）
  const total = detail.poolN.spring + detail.poolN.summer + detail.poolN.autumn + detail.poolN.winter;
  check('职业池事件总数 = 446（原 398 + 48）', total === 446, String(total));
});
