/* 静态代码审查（AST 级）
 *
 * 这个游戏是"零依赖单文件"，没有构建期检查——很多 bug 属于"不报错但不对"：
 * 未注册的效果键只 console.warn、拼错的跳转目标静默失效、
 * 重复的函数声明后者悄悄覆盖前者、死代码永远不出现。
 * 这里用 acorn 把整份脚本解析成 AST，逐类扫。
 */
const fs = require('fs');
const path = require('path');
const acorn = require('acorn');
const walk = require('acorn-walk');
const { JSDOM, VirtualConsole } = require('jsdom');

const HTML = require('./testkit').resolveHtml();
const html = fs.readFileSync(HTML, 'utf8');
console.log('审查对象: ' + path.relative(process.cwd(), HTML));
const src = html.match(/<script>([\s\S]*?)<\/script>/)[1];

const findings = [];
const add = (level, cat, msg, extra) => findings.push({ level, cat, msg, extra });

// ── 解析 ────────────────────────────────────────────────
let ast;
try {
  ast = acorn.parse(src, { ecmaVersion: 'latest', sourceType: 'script', locations: true });
} catch (e) {
  console.log('AST 解析失败:', e.message);
  process.exit(1);
}
const lineOf = node => (node.loc ? node.loc.start.line : 0);

// ── 1. 顶层重复声明（重复 function 不会报错，后者静默覆盖前者）──
const topFuncs = {};
for (const node of ast.body) {
  if (node.type === 'FunctionDeclaration' && node.id) {
    (topFuncs[node.id.name] = topFuncs[node.id.name] || []).push(lineOf(node));
  }
}
Object.entries(topFuncs).forEach(([n, lines]) => {
  if (lines.length > 1) add('HIGH', '重复声明', `顶层函数 ${n}() 声明了 ${lines.length} 次（第 ${lines.join(', ')} 行），只有最后一次生效`);
});

// ── 2. 收集所有 fx 对象的键 / next 目标 / 事件 id ──────────
const fxKeys = new Set();
const nextTargets = [];
const eventIds = [];
const eventIdLines = [];

walk.full(ast, node => {
  if (node.type === 'Property' && node.key && node.key.name === 'fx' && node.value && node.value.type === 'ObjectExpression') {
    node.value.properties.forEach(p => {
      const k = p.key && (p.key.name || p.key.value);
      if (k) fxKeys.add(k);
      if (p.key && p.key.name && !['calculated'].includes(p.key.type) === false) { /* noop */ }
    });
  }
  if (node.type === 'Property' && node.key && node.key.name === 'next' && node.value && node.value.type === 'Literal') {
    nextTargets.push({ target: node.value.value, line: lineOf(node) });
  }
  // evt('id', ...) / story('id', ...)
  if (node.type === 'CallExpression' && node.callee && (node.callee.name === 'evt' || node.callee.name === 'story')) {
    const a0 = node.arguments[0];
    if (a0 && a0.type === 'Literal') { eventIds.push(a0.value); eventIdLines.push([a0.value, lineOf(node)]); }
  }
});

// ── 2.5 同一状态对象有多处构造点？字段集合不一致就是 bug ────
// 这类 bug 不报错：少构造一个字段，下游读到时是 undefined，功能只是"悄悄不生效"。
/* 已人工确认的可选判别字段：按分支需要出现，消费端都有兜底，不算漏字段。
 * _playoffResult.kind / .level —— computeSeason 里两者都是可选判别：
 *   kind 'march' 走疯狂三月分支、'playin' 走附加赛分支，取不到时用 rounds 兜底；
 *   7 个构造点分别对应联盟冠军 / 联盟出局 / 疯狂三月 / 附加赛，字段组合本来就不同。 */
const OPTIONAL_KEYS = {};   /* v4.12：_playoffResult 已收敛 makePlayoffResult() 工厂，各构造点字段一致，白名单清空 */
const buildSites = {};
walk.full(ast, node => {
  if (node.type !== 'AssignmentExpression') return;
  const L = node.left, Rr = node.right;
  if (!L || L.type !== 'MemberExpression' || !Rr || Rr.type !== 'ObjectExpression') return;
  if (!L.object || L.object.type !== 'Identifier' || L.object.name !== 'S') return;
  const prop = L.property && (L.property.name || L.property.value);
  if (!prop || L.computed) return;
  const keys = Rr.properties.filter(p => p.type === 'Property' && !p.computed)
    .map(p => p.key.name || p.key.value);
  (buildSites[prop] = buildSites[prop] || []).push({ line: lineOf(node), keys: new Set(keys) });
});
let dynSites = 0, compared = 0;
Object.entries(buildSites).forEach(([prop, sites]) => {
  // 空字面量 `S.x={}` 是"先建再填"的写法（后面常跟 forEach 赋值），静态看不到最终字段，不参与比对
  const concrete = sites.filter(x => x.keys.size > 0);
  dynSites += sites.length - concrete.length;
  if (concrete.length < 2) return;
  compared++;
  const opt = OPTIONAL_KEYS[prop] || [];
  const all = new Set(); concrete.forEach(x => x.keys.forEach(k => all.add(k)));
  concrete.forEach(x => {
    const miss = [...all].filter(k => !x.keys.has(k) && opt.indexOf(k) < 0);
    if (miss.length) add('MED', '构造点字段',
      `S.${prop} 在第 ${x.line} 行少了 ${miss.length} 个字段: ${miss.join(', ')}（其它构造点有；若为可选判别字段请加进 OPTIONAL_KEYS）`);
  });
});
if (!findings.some(f => f.cat === '构造点字段')) {
  add('OK', '构造点一致性', `${compared} 组状态对象的构造点字段集合一致（跳过 ${dynSites} 处先建再填的空字面量）`);
}

// ── 2.7 R.pick(数组.filter(...)) 可能拿到空数组 ────────────
// R.pick 对空数组返回 undefined，配上模板字符串就会渲染出 "undefined"。
let emptyPickRisk = 0;
walk.full(ast, node => {
  if (node.type !== 'CallExpression' || !node.callee || node.callee.name !== 'R.pick') return;
  const a = node.arguments[0];
  if (a && a.type === 'CallExpression' && a.callee && a.callee.property && a.callee.property.name === 'filter') {
    emptyPickRisk++;
  }
});
add(emptyPickRisk ? 'MED' : 'OK', '空数组取值',
  emptyPickRisk ? `${emptyPickRisk} 处 R.pick(x.filter(...)) 在筛选结果为空时会拿到 undefined`
                : '没有 R.pick(筛选结果) 这种可能取到 undefined 的写法');

// ── 3. 运行时真值：从 jsdom 取注册表 ──────────────────────
const vc = new VirtualConsole();
const rt = [];
vc.on('jsdomError', e => { const m = e.message || ''; if (!/scrollTo|scrollIntoView|Not implemented/.test(m)) rt.push(m); });
function stubAudio() {
  class AC {
    constructor() { this.destination = {}; this.currentTime = 0; }
    createGain() { return { gain: { value: 1 }, connect() {}, disconnect() {} }; }
    createOscillator() { return { type: '', frequency: { value: 0 }, connect() {}, start() {}, stop() {}, disconnect() {} }; }
    createBiquadFilter() { return { type: '', frequency: { value: 0 }, Q: { value: 0 }, connect() {}, disconnect() {} }; }
    createDelay() { return { delayTime: { value: 0 }, connect() {}, disconnect() {} }; }
    createDynamicsCompressor() { return { threshold: { value: 0 }, knee: { value: 0 }, ratio: { value: 0 }, attack: { value: 0 }, release: { value: 0 }, connect() {}, disconnect() {} }; }
    createStereoPanner() { return { pan: { value: 0 }, connect() {}, disconnect() {} }; }
    createConvolver() { return { buffer: null, connect() {}, disconnect() {} }; }
    createBuffer() { return { getChannelData() { return new Float32Array(1); } }; }
  }
  return AC;
}
const dom = new JSDOM(html, {
  runScripts: 'dangerously', pretendToBeVisual: true, virtualConsole: vc, url: 'https://x.local/',
  beforeParse(win) {
    win.AudioContext = stubAudio(); win.webkitAudioContext = stubAudio();
    win.URL.createObjectURL = () => 'blob:t'; win.URL.revokeObjectURL = () => {};
    win.confirm = () => true;
  },
});
const win = dom.window;

module.exports = new Promise(resolve => setTimeout(() => {
  const R = JSON.parse(win.eval(`JSON.stringify({
    fx: FX.map(p=>p[0]),
    evfns: Object.keys(EVFNS),
    story: Object.keys(STORY),
    pools: Object.fromEntries(['spring','summer','autumn','winter','youthSpring','youthSummer','youthAutumn','youthWinter'].map(k=>[k,(POOLS[k]||[]).map(e=>e.id)])),
    gated: Object.keys(GATED),
    kind: Object.keys(EV_KIND_OVERRIDE),
    ids: (function(){const s={};['spring','summer','autumn','winter','youthSpring','youthSummer','youthAutumn','youthWinter'].forEach(k=>(POOLS[k]||[]).forEach(e=>{s[e.id]=(s[e.id]||0)+1;}));Object.keys(STORY).forEach(k=>{s[k]=(s[k]||0)+1;});return s;})()
  })`));

  // 1) fx 键
  const fxSet = new Set(R.fx);
  const badFx = [...fxKeys].filter(k => !fxSet.has(k));
  if (badFx.length) add('HIGH', '效果键', `有 ${badFx.length} 个 fx 键既不在 FX 注册表、也没人消费（选项等于没效果）: ${badFx.join(', ')}`);
  else add('OK', '效果键', `全部 ${fxKeys.size} 个 fx 键都已在注册表登记`);

  // 2) next 目标
  const allTargets = new Set([...R.evfns, ...R.story, ...R.ids ? Object.keys(R.ids) : []]);
  const badNext = nextTargets.filter(t => !allTargets.has(t.target));
  if (badNext.length) add('HIGH', '跳转', `有 ${badNext.length} 处 next 指向不存在的 id: ${badNext.map(t => t.target + '(第' + t.line + '行)').join(', ')}`);
  else add('OK', '跳转', `全部 ${nextTargets.length} 处 next 目标都能解析`);

  // 3) 事件 id 重复
  const dupIds = Object.entries(R.ids).filter(([, n]) => n > 1).map(([k, n]) => k + '×' + n);
  if (dupIds.length) add('HIGH', '事件 id', `事件 id 重复：${dupIds.join(', ')}（会让 S.used 去重记错、图鉴计数不对）`);
  else add('OK', '事件 id', `全部 ${Object.keys(R.ids).length} 个事件 id 唯一`);

  // 4) GATED / EV_KIND_OVERRIDE 指向不存在的事件
  const idSet = new Set(Object.keys(R.ids));
  const badGate = R.gated.filter(id => !idSet.has(id));
  const badKind = R.kind.filter(id => !idSet.has(id));
  if (badGate.length) add('MED', '门槛表', `GATED 里有 ${badGate.length} 个 id 不存在对应事件: ${badGate.join(', ')}（死配置）`);
  if (badKind.length) add('MED', '分档表', `EV_KIND_OVERRIDE 里有 ${badKind.length} 个 id 不存在对应事件: ${badKind.join(', ')}（死配置）`);
  if (!badGate.length && !badKind.length) add('OK', '配置表', 'GATED / EV_KIND_OVERRIDE 没有指向不存在的事件');

  // 5) 死代码：声明了但全文件只出现一次的函数
  const deadFns = [];
  Object.keys(topFuncs).forEach(n => {
    const re = new RegExp('\\b' + n.replace(/\$/g, '\\$') + '\\b', 'g');
    const cnt = (src.match(re) || []).length;
    if (cnt <= 1) deadFns.push(n + '(第' + topFuncs[n][0] + '行)');
  });
  if (deadFns.length) add('MED', '死代码', `${deadFns.length} 个顶层函数全文件只出现一次（无人调用）: ${deadFns.join(', ')}`);
  else add('OK', '死代码', '没有从未被引用的顶层函数');

  // 6) 空 catch（吞异常）
  let emptyCatch = 0;
  walk.full(ast, node => {
    if (node.type === 'CatchClause' && node.body.body.length === 0) emptyCatch++;
  });
  add(emptyCatch > 12 ? 'MED' : 'INFO', '异常吞噬', `空 catch 块 ${emptyCatch} 处`);

  // 7) 事件池规模与四季均衡
  const sizes = ['spring', 'summer', 'autumn', 'winter'].map(k => k + '=' + R.pools[k].length);
  add('INFO', '事件池', `职业四季：${sizes.join(' ')} ｜ 青训四季：` +
    ['youthSpring', 'youthSummer', 'youthAutumn', 'youthWinter'].map(k => k + '=' + R.pools[k].length).join(' '));

  // ── 输出 ─────────────────────────────────────────────
  const order = { HIGH: 0, MED: 1, INFO: 2, OK: 3 };
  findings.sort((a, b) => order[a.level] - order[b.level]);
  const icon = { HIGH: '❌', MED: '⚠️ ', INFO: 'ℹ️ ', OK: '✅' };
  for (const f of findings) console.log(`${icon[f.level]} [${f.cat}] ${f.msg}`);
  if (rt.length) console.log('\n运行时异常:', rt.slice(0, 3).join(' | '));
  const bad = findings.filter(f => f.level === 'HIGH').length;
  console.log('\n严重问题 ' + bad + ' 项' + (bad ? ' ← 不要提交' : ''));
  if (bad) console.log('\n（误报就往 OPTIONAL_KEYS 白名单里加，并在注释里写清为什么可选）');
  const summary = { name: 'AST 审查', ok: bad === 0, passed: findings.filter(f => f.level !== 'HIGH').length,
                    total: findings.length, line: '严重问题 ' + bad + ' 项' };
  resolve(summary);
  if (require.main === module) process.exit(bad ? 1 : 0);
}, 1200));
