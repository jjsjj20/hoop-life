/* 测试公共脚手架
 *
 * 抽出来的原因：6 个测试脚本各自重复一遍 jsdom 装配、AudioContext 桩、断言收集、
 * 结果打印——重复的样板越多，"再加一个测试"的成本越高，安全网就越难长大。
 *
 * 用法：
 *   const { run } = require('./testkit');
 *   run('冒烟', ({ win, doc, check, errors }) => {
 *     check('xxx', cond, '出问题时的补充信息');
 *   });
 *
 * 被测文件解析顺序（谁先存在用谁）：
 *   1. 环境变量 GAME_HTML
 *   2. ../篮球人生.html        ← CI 里仓库根就是这个
 *   3. ../output/篮球人生.html ← 本地构建产物
 */
const fs = require('fs');
const path = require('path');
const { JSDOM, VirtualConsole } = require('jsdom');

const HERE = __dirname;

function resolveHtml(explicit) {
  const cands = [explicit, process.env.GAME_HTML,
    path.resolve(HERE, '..', '篮球人生.html'),
    path.resolve(HERE, '..', 'output', '篮球人生.html')].filter(Boolean);
  for (const c of cands) if (fs.existsSync(c)) return c;
  console.error('找不到被测文件，试过：\n  ' + cands.join('\n  '));
  process.exit(2);
}

/* WebAudio 桩：游戏用振荡器现场合成音效，jsdom 没有 AudioContext。
 * 每个方法都返回带 connect/disconnect 的空壳，够游戏跑完初始化与播放路径。 */
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

const IGNORE = /scrollTo|scrollIntoView|Not implemented/;

/* 两种用法：
 *   直接跑（node tools/test_x.js）      → 打完结果自己 process.exit
 *   被 verify_all.js require（COLLECT）→ 不 exit，把结果 resolve 出去，由汇总脚本统一退出
 * 之所以不做成"每个测试起一个子进程"：同进程顺序跑更简单，而且行为在本地与 CI 完全一致。 */
const COLLECT = process.env.TESTKIT_COLLECT === '1';

function run(name, body, opts) {
  opts = opts || {};
  const file = resolveHtml(opts.html);
  const html = fs.readFileSync(file, 'utf8');
  // errors：所有异常（jsdomError + console.error），用于断言"无未捕获异常"
  // consoleErrors：只收 console.error，用于断言"崩溃日志确实打到了控制台"
  const errors = [], consoleErrors = [], warns = [];
  const vc = new VirtualConsole();
  vc.on('jsdomError', e => { const m = e.message || String(e); if (!IGNORE.test(m)) errors.push(m); });
  vc.on('error', m => { consoleErrors.push(String(m)); errors.push(String(m)); });
  vc.on('warn', m => warns.push(String(m)));

  const dom = new JSDOM(html, {
    runScripts: 'dangerously', pretendToBeVisual: true, virtualConsole: vc,
    url: 'https://x.local/',
    beforeParse(win) {
      win.AudioContext = stubAudio();
      win.webkitAudioContext = stubAudio();
      win.URL.createObjectURL = () => 'blob:test';
      win.URL.revokeObjectURL = () => {};
      win.confirm = () => true;
    },
  });
  const win = dom.window, doc = win.document;

  const results = [];
  const check = (n, cond, extra) => { results.push({ n, ok: !!cond, extra }); };
  /* 键盘交互辅助：绝大多数交互测试都要按一下键 */
  const key = k => doc.dispatchEvent(new win.KeyboardEvent('keydown', { key: k, bubbles: true, cancelable: true }));
  /* 鼠标点击辅助 */
  const click = el => el && el.dispatchEvent(new win.MouseEvent('click', { bubbles: true }));

  return new Promise(resolve => setTimeout(async () => {
    try {
      const r = body({ win, doc, check, errors, consoleErrors, warns, html, file, key, click });
      if (r && typeof r.then === 'function') await r;
    } catch (e) {
      check('测试体本身未抛异常', false, (e && e.stack || String(e)).split('\n').slice(0, 4).join(' | '));
    }
    let fail = 0;
    for (const r of results) {
      if (!r.ok) fail++;
      console.log((r.ok ? 'PASS  ' : 'FAIL  ') + r.n + (r.ok || !r.extra ? '' : '   → ' + r.extra));
    }
    if (errors.length) console.log('\n未捕获异常:\n  ' + errors.slice(0, 5).join('\n  '));
    console.log('\n══ ' + name + ': ' + (results.length - fail) + '/' + results.length + ' 通过');
    const summary = { name: name, ok: fail === 0, passed: results.length - fail, total: results.length,
                      line: (results.length - fail) + '/' + results.length + ' 通过' };
    resolve(summary);
    if (!COLLECT) process.exit(fail ? 1 : 0);
  }, opts.ready == null ? 1200 : opts.ready));
}

module.exports = { run, stubAudio, resolveHtml };
