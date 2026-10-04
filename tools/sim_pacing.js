/* M1/P2：签位事件复活后的节奏复核
 *
 * 做法：不开 DOM，直接驱动游戏函数（getEvent/choose/advance/nextYear…），
 * 连续推进 30 个不同天赋与联赛的生涯，逐季记录：
 *   · 每季事件数（S.evSeen）
 *   · 戏剧占比（S.evDrama / S.evSeen）
 *   · 题材覆盖（S.usedTopics，游戏内已去重，真实查重用 analyze_pacing.js 的 id→题材映射）
 *   · 事件 id 的跨季重复率（对照 S.recent 的 4 年规则）
 * 验收线（开发计划 P2 原文写「每季 2~4」，复核后确认 v4.8 原版的 stageNeedFor
 * 是「每阶段」2~4 —— 一季 4 阶段，每季 8~16 才是原设计节奏）：
 *   戏剧占比 ≥ 30%（生涯前 20 季窗口）· 同季题材重复可接受（故事 > 题材）·
 *   4 年重复率 < 5%
 *
 * 内存提示：游戏在 jsdom 里长期执行会累积内存，一个进程跑 30 个生涯必 OOM。
 * 内存受限的环境用「一个生涯一个进程」：
 *   for i in 0..29: SIM_ONE=$i node tools/sim_pacing.js   →  sim_part_$i.json
 *   node tools/merge_sim.js                               →  sim_raw.json
 */
const fs = require('fs');
const path = require('path');
const { JSDOM, VirtualConsole } = require('jsdom');

const FILE = process.env.GAME_HTML
  || [path.resolve(__dirname, '..', '篮球人生.html'),          // 脚本在 repo/tools/ 时
      path.resolve(__dirname, '..', 'repo', '篮球人生.html')]  // 脚本在工作区 build/ 时
     .find(f => fs.existsSync(f));
if (!FILE) { console.error('找不到游戏文件 篮球人生.html'); process.exit(2); }
const html = fs.readFileSync(FILE, 'utf8');

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

const errors = [];
const vc = new VirtualConsole();
vc.on('jsdomError', e => { const m = e.message || ''; if (!/Not implemented|scrollTo|scrollIntoView/.test(m)) errors.push(m); });

const dom = new JSDOM(html, {
  runScripts: 'dangerously', pretendToBeVisual: true, virtualConsole: vc, url: 'https://x.local/',
  beforeParse(w) {
    w.AudioContext = stubAudio(); w.webkitAudioContext = stubAudio();
    w.URL.createObjectURL = () => 'blob:t'; w.URL.revokeObjectURL = () => {};
    w.confirm = () => true;
  },
});
const win = dom.window;

// ── 配置：30 个生涯，覆盖不同联赛/模式/天赋 ──
const N = Number(process.env.SIM_N || 30);
const careers = [];
for (let i = 0; i < N; i++) {
  careers.push({
    league: ['NBA', 'CBA', '欧洲'][i % 3],
    mode: i % 5 === 4 ? 'fast' : 'immersive',
    ovrHint: 60 + (i % 25),
    tag: '#' + i,
  });
}

const SUMMARIES = [];

/* 单生涯模式：SIM_ONE=<index> 只跑 careers[index]，写出 sim_part_<index>.json。
 * 游戏在 jsdom 里长期执行会累积内存（30 生涯一个进程必 OOM），
 * 内存受限的环境用 bash 循环「一个生涯一个进程」，最后用 merge_sim.js 合并。 */
const ONE = process.env.SIM_ONE;

const AGE_INIT = Number(process.env.SIM_AGE || 18);   /* R2：SIM_AGE=15 青训起步 */
const YOUTH = AGE_INIT < 18;

function runCareer(cfg) {
  win.eval(`JSON.stringify((function(){
    // 重新开一局
    renderCreate();
    document.getElementById('fName').value='模拟${cfg.tag}';
    doCreate(); allocRandom(); confirmAlloc();
    // 按配置摆联赛与模式
    S.age=${AGE_INIT}; S.league=${JSON.stringify(YOUTH?'青训':cfg.league)}; S.mode=${JSON.stringify(cfg.mode)};
    ${YOUTH ? "S.team='山东高速青年队';S.teamStr=4;" : "S.team=TEAMS[S.league==='NBA'?'nba':S.league==='CBA'?'cba':'euro'][0][0];S.teamStr=6;"}
    S.stage='spring'; S.stageDone=0; S.stageNeed=stageNeedFor();
    ensureWorld(); if(isPro()&&!S.contract)setContract(S.team,S.league,2,'职业合同');
    // 高能力：让职业生涯能走很长（方便看长期节奏）
    SKILLS.forEach(p=>{S.skills[p[0]]=${cfg.ovrHint};});
    for(const k in S.a)S.a[k]=${cfg.ovrHint};
    S.evY=null;S.evSeen=0;S.evDrama=0;S.usedTopics=[];S.used={};S.recent={};
    return {evY:(S.birthYear+S.age),age:S.age,league:S.league,mode:S.mode};
  })())`);
  // 逐季推进并记录
  const seasons = [];
  let cur = null;
  for (let step = 0; step < 4000; step++) {
    const m = win.__mode();
    if (m === 'end') break;
    // 在「事件」模式下先快照本季统计（evY 变化时统计会被重置）
    if (m === 'event') {
      const o = JSON.parse(win.__snap());
      if (cur) {
        if (o.evY !== cur.evY) {           // 新的一季开始了 → 记录刚结束的那一季
          seasons.push(cur); cur = null;
        }
      }
      if (!cur) cur = { evY: o.evY, seen: 0, drama: 0, topics: o.topics.slice(), ids: [] };
      cur.seen = o.seen; cur.drama = o.drama; cur.topics = o.topics.slice(); cur.ids = o.ids.slice();
    }
    win.__step();
  }
  if (cur) seasons.push(cur);
  return { tag: cfg.tag, league: cfg.league, mode: cfg.mode, seasons };
}

setTimeout(() => {
  /* 热循环里绝不能反复 win.eval（每步编译新脚本）——
   * 每步要用的代码只编译一次，挂到 window 上反复调用 */
  win.eval(`
    window.__mode=function(){return UI&&UI.mode;};
    /* S.used 是跨季累计结构（按池子耗尽才清），不能当本季事件用；
     * S.recent[id]=抽中年份，按当年过滤即为本季真实抽到的池事件 id */
    window.__snap=function(){return JSON.stringify({evY:S.evY,seen:S.evSeen,drama:S.evDrama,topics:S.usedTopics.slice(),ids:Object.keys(S.recent||{}).filter(function(id){return S.recent[id]===S.evY;})});};
    window.__step=function(){(function(){
      const m=UI&&UI.mode;
      if(m==='event'){const ev=UI.ev;if(ev&&ev.choices&&ev.choices.length){choose(R.int(0,ev.choices.length-1));}else{UI.ev=getEvent();}}
      else if(m==='result'){advance();}
      else if(m==='season'){nextYear();}
      else if(m==='awards'){awardsNext();}
      else {UI={mode:'event',ev:getEvent()};}
    })();};
  `);
  win.eval('renderCreate();');
  dom.window.document.querySelector('#fName').value = '模拟';
  win.eval('doCreate(); allocRandom(); confirmAlloc();');

  if (ONE !== undefined && ONE !== '') {
    const i = Number(ONE);
    const r = runCareer(careers[i]);
    fs.writeFileSync(path.resolve(__dirname, 'sim_part_' + i + '.json'), JSON.stringify(r));
    console.log('分片 ' + i + ' 完成：' + r.seasons.length + ' 个赛季');
    process.exit(0);
  }

  for (const cfg of careers) {
    SUMMARIES.push(runCareer(cfg));
  }

  fs.writeFileSync(path.resolve(__dirname, 'sim_raw.json'), JSON.stringify(SUMMARIES));
  console.log('模拟完成：' + SUMMARIES.length + ' 个生涯，共 ' +
    SUMMARIES.reduce((n, c) => n + c.seasons.length, 0) + ' 个赛季');
  process.exit(0);
}, 1200);
