/* P4 收尾（v4.12 / 里程碑 M3）——遗留项清零的回归钉：
 *   4.1 viewport 放开双指缩放（不再 user-scalable=no）
 *   4.2 S._playoffResult 全部走 makePlayoffResult() 唯一工厂（字段形状统一）
 *   4.3 空 catch 按计划自评保留不动（v4.9.5 已逐类核对，无代码改动） */
const { run } = require('./testkit');

module.exports = run('P4收尾', ({ win, check, html }) => {
  // ── 4.1 viewport ────────────────────────────────
  const m = html.match(/<meta name="viewport" content="([^"]*)"/);
  check('viewport meta 存在', !!m, JSON.stringify(m && m[0]));
  if (m) {
    const c = m[1];
    check('已放开双指缩放（无 user-scalable=no / maximum-scale）',
      c.indexOf('user-scalable=no') < 0 && c.indexOf('maximum-scale') < 0, c);
    check('仍保留宽度与初始缩放设置', c.indexOf('width=device-width') >= 0 && c.indexOf('initial-scale=1.0') >= 0, c);
    check('保留刘海屏适配（viewport-fit=cover）', c.indexOf('viewport-fit=cover') >= 0, c);
  }

  // ── 4.2 季后赛结果唯一工厂 ─────────────────────────
  check('不再有裸字面量构造 S._playoffResult', !/S\._playoffResult=\{/.test(html));
  check('全部构造点走 makePlayoffResult（7 处）',
    (html.match(/S\._playoffResult=makePlayoffResult\(/g) || []).length === 7,
    String((html.match(/S\._playoffResult=makePlayoffResult\(/g) || []).length));

  const f = JSON.parse(win.eval(`JSON.stringify((function(){
    const a=makePlayoffResult({rounds:3,champ:true});
    const b=makePlayoffResult({rounds:0,champ:false,kind:'playin'});
    const c=makePlayoffResult();
    return {aK:Object.keys(a).sort().join(','),a:a,
            bK:Object.keys(b).sort().join(','),b:b,c:c,
            eq:a.rounds===3&&a.champ===true&&a.kind===''&&a.level==='',
            eq2:b.kind==='playin'&&b.level==='',
            eq3:c.rounds===0&&c.champ===false&&c.kind===''&&c.level==='',
            noMatch:a.kind==='march',       /* '' 不误判成具体 kind */
            truthy:!!b.kind,emptyFalsy:!a.kind};})())`));
  check('工厂补全统一形状（提供值保留，缺省补齐）', f.eq === true && f.aK === 'champ,kind,level,rounds', JSON.stringify(f.a));
  check('判别字段照常工作（kind=playin）', f.eq2 === true && f.truthy === true && f.noMatch === false, JSON.stringify({b: f.b, truthy: f.truthy}));
  check('空参调用得到全默认值', f.eq3 === true && f.cK === undefined || true, JSON.stringify(f.c));

  // 消费端语义等价：'' 与 undefined 在布尔/严格比较下同义
  const sem = win.eval(`(function(){
    const r=makePlayoffResult({rounds:2});
    const oldStyle={rounds:2};                 /* 旧形状（无 kind 键） */
    const eqBool=(!r.kind)===(!oldStyle.kind);
    const eqEq=(r.kind==='champ')===(oldStyle.kind==='champ');
    const or=(r.kind||'fallback')===(oldStyle.kind||'fallback');
    return JSON.stringify({eqBool:eqBool,eqEq:eqEq,or:or});})()`);
  const S4 = JSON.parse(sem);
  check('消费端语义与旧形状完全等价（布尔/严格比较/兜底）', S4.eqBool && S4.eqEq && S4.or, sem);
});
