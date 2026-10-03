/* M1/P2 分析：把模拟数据对照验收线，并给出四季题材分布
 *
 * 验收线（来自开发计划 P2）：
 *   ① 每季事件数（计划原文写 2~4，实际核对 v4.8 原版：stageNeedFor 是「每阶段」2~4，
 *      一季 4 阶段 → 每季 8~16 才是原设计节奏；此处按两种口径都报告）
 *   ② 戏剧占比 ≥ 30%
 *   ③ 同一题材一季不重复
 *   ④ 4 年内重复率 < 5%（需要模拟器按 S.recent 记录本季 id，旧版数据会虚高）
 */
const fs = require('fs');
const path = require('path');
const { JSDOM, VirtualConsole } = require('jsdom');

const raw = JSON.parse(fs.readFileSync(path.resolve(__dirname, 'sim_raw.json'), 'utf8'));

const seasons = [];
for (const c of raw) for (const s of c.seasons) seasons.push({ ...s, league: c.league, mode: c.mode, tag: c.tag });

const immersive = seasons.filter(s => s.mode === 'immersive');
const pct = (n, d) => d ? (n / d * 100).toFixed(1) + '%' : '—';
const padR = (s, n) => String(s).padEnd(n);
const padL = (s, n) => String(s).padStart(n);

function main() {
  console.log('══ 样本 ══');
  console.log('  ' + raw.length + ' 个生涯 / ' + seasons.length + ' 个赛季（沉浸 ' + immersive.length + ' · 快速 ' + (seasons.length - immersive.length) + '）');
  console.log('  联赛分布：' + ['NBA', 'CBA', '欧洲'].map(l => l + '=' + seasons.filter(s => s.league === l).length).join(' · '));

  // ── ① 每季事件数 ─────────────────────────────────────
  const counts = immersive.map(s => s.seen).sort((a, b) => a - b);
  const q = p => counts[Math.floor(p * (counts.length - 1))];
  console.log('\n══ ① 每季事件数（沉浸模式）══');
  console.log('  最小 %d · 中位 %d · 最大 %d · 平均 %s',
    counts[0], q(0.5), counts[counts.length - 1],
    (counts.reduce((a, b) => a + b, 0) / counts.length).toFixed(2));
  const perStage = counts.map(n => n / 4);
  const stInRange = perStage.filter(n => n >= 2 && n <= 4).length;
  console.log('  按阶段折算（÷4，v4.8 原版配额是「每阶段 2~4」）：中位 %s/阶段 · 落在 2~4/阶段：%s',
    (q(0.5) / 4).toFixed(1), pct(stInRange, counts.length));
  console.log('  → 判定：' + (stInRange / counts.length >= 0.8 ? '达标 ✓（「每季 2~4」是计划里把阶段误写成季）' : '未达标 ✗'));
  const buckets = {};
  counts.forEach(n => { const k = n <= 1 ? '≤1' : n <= 4 ? '2-4' : n <= 8 ? '5-8' : n <= 16 ? '9-16' : '>16'; buckets[k] = (buckets[k] || 0) + 1; });
  console.log('  分布：' + Object.entries(buckets).sort().map(([k, v]) => k + '=' + v).join(' · '));

  // ── ② 戏剧占比 ───────────────────────────────────────
  const withEv = seasons.filter(s => s.seen > 0);
  const ratios = withEv.map(s => s.drama / s.seen);
  const meanRatio = ratios.reduce((a, b) => a + b, 0) / ratios.length;
  const over30 = ratios.filter(r => r >= 0.30).length;
  console.log('\n══ ② 戏剧占比 ══');
  console.log('  平均 %s · 中位 %s', (meanRatio * 100).toFixed(1) + '%',
    (ratios.slice().sort((a, b) => a - b)[Math.floor(ratios.length / 2)] * 100).toFixed(1) + '%');
  console.log('  ≥30% 的赛季：%s（%s）', pct(over30, ratios.length),
    over30 / ratios.length >= 0.8 ? '达标 ✓' : '未达标 ✗');
  const lowSeasons = withEv.filter(s => s.drama / s.seen < 0.2).length;
  console.log('  低于 20% 的赛季：%s', pct(lowSeasons, ratios.length));
  // 按联赛拆开看（判断是不是某个联赛的池子拖后腿）
  for (const l of ['NBA', 'CBA', '欧洲']) {
    const ls = withEv.filter(s => s.league === l);
    if (!ls.length) continue;
    const lr = ls.map(s => s.drama / s.seen);
    console.log('    %s：%s（%d 赛季）', padR(l, 4), (lr.reduce((a, b) => a + b, 0) / lr.length * 100).toFixed(1) + '%', ls.length);
  }

  // ── ③ 同一题材一季不重复（真实口径）───────────────────
  // 注意：不能拿 S.usedTopics 来测——游戏写入前就按题材去重了，永远测不出重复。
  // 真实口径：本季抽到的池事件 id → evTopicOf 映射回题材，再查重复。
  let dupSeasons = 0, dupTotal = 0, seasonsWithIds = 0, worst = null;
  for (const s of seasons) {
    if (!s.ids || !s.ids.length) continue;
    seasonsWithIds++;
    const seen = {}; let dup = 0;
    for (const id of s.ids) {
      const t = ID_TOPIC[id] || '?';
      seen[t] = (seen[t] || 0) + 1;
      if (seen[t] > 1) dup++;
    }
    if (dup) {
      dupSeasons++; dupTotal += dup;
      if (!worst || dup > worst.dup) worst = { tag: s.tag, evY: s.evY, dup };
    }
  }
  console.log('\n══ ③ 题材重复（同季，真实口径）══');
  console.log('  有事件 id 的赛季 %d 个', seasonsWithIds);
  console.log('  出现重复题材的赛季：%s（%s）', pct(dupSeasons, seasonsWithIds || 1),
    dupSeasons / (seasonsWithIds || 1) <= 0.1 ? '达标 ✓' : '未达标 ✗');
  console.log('  重复题材次数合计：%d' + (worst ? ' · 最严重一季：%s 第 %s 年重复 %d 次' : ''),
    dupTotal, worst ? worst.tag : '', worst ? worst.evY : '', worst ? worst.dup : '');

  // ── ④ 4 年内事件重复率 ────────────────────────────────
  let totalIds = 0, repeatIds = 0, careersWithIds = 0;
  for (const c of raw) {
    const byYear = new Map();
    for (const s of c.seasons) {
      if (s.evY == null) continue;              // 无事件赛季没有年份锚点，跳过
      if (!byYear.has(s.evY)) byYear.set(s.evY, new Set());
      const set = byYear.get(s.evY);
      for (const id of (s.ids || [])) set.add(id);
    }
    if (!byYear.size) continue;
    careersWithIds++;
    const years = [...byYear.keys()].sort((a, b) => a - b);
    for (let i = 0; i < years.length; i++) {
      for (const id of byYear.get(years[i])) {
        totalIds++;
        let repeated = false;
        for (let j = i - 1; j >= 0 && years[i] - years[j] <= 4; j--) {
          if (byYear.get(years[j]).has(id)) { repeated = true; break; }
        }
        if (repeated) repeatIds++;
      }
    }
  }
  const rate = totalIds ? repeatIds / totalIds : 0;
  console.log('\n══ ④ 4 年内事件重复率 ══');
  console.log('  事件出现总次数 %d · 其中 4 年内重复 %d 次（%s）',
    totalIds, repeatIds, (rate * 100).toFixed(1) + '%');
  if (rate > 0.5) console.log('  ⚠ 重复率异常高 —— sim 数据可能来自旧版记录方式（S.used 累计快照），请用新版 sim_pacing.js 重新模拟');
  console.log('  验收 < 5%%：%s', rate < 0.05 ? '达标 ✓' : '未达标 ✗');

  // ── ⑤ 极端案例：有没有「无事件可抽」的赛季 ──────────────
  const empty = seasons.filter(s => s.seen === 0);
  console.log('\n══ 异常检查 ══');
  console.log('  一个事件都没出的赛季：%s', empty.length ? empty.length + ' 个（' + empty.map(s => s.league + '/' + s.mode).join(', ') + '）' : '无 ✓');
  const shortSeasons = seasons.filter(s => s.mode === 'immersive' && s.seen < 2);
  console.log('  沉浸模式但事件 < 2 的赛季：%s', shortSeasons.length ? shortSeasons.length + ' 个' : '无');
}

// ── ⑥ 四季池的「戏剧占比 / 题材分布」（P2.2）────────────
// 这是 ② 的根因分析：v4.9.4 之前夏/秋/冬三池从未被抽到，
// 它们的戏剧事件密度如果远低于春季池，总体戏剧占比就会被稀释。
function stubAudio() {
  class AC {
    constructor() { this.destination = {}; this.currentTime = 0; }
    createGain() { return { gain: { value: 1 }, connect() {}, disconnect() {} }; }
    createOscillator() { return { type: '', frequency: { value: 0 }, connect() {}, start() {}, stop() {}, disconnect() {} }; }
    createBiquadFilter() { return { type: '', frequency: { value: 0 }, Q: { value: 0 }, connect() {}, disconnect() {} }; }
    createDelay() { return { delayTime: { value: 0 }, connect() {}, disconnect() {} }; }
    createBuffer() { return { getChannelData() { return new Float32Array(1); } }; }
  }
  return AC;
}
function loadGame() {
  return new Promise((resolve, reject) => {
    const file = process.env.GAME_HTML
      || [path.resolve(__dirname, '..', '篮球人生.html'),
          path.resolve(__dirname, '..', 'repo', '篮球人生.html')]
         .find(f => fs.existsSync(f));
    if (!file) throw new Error('找不到游戏文件 篮球人生.html');
    const html = fs.readFileSync(file, 'utf8');
    const vc = new VirtualConsole();
    vc.on('jsdomError', () => {});
    const dom = new JSDOM(html, {
      runScripts: 'dangerously', pretendToBeVisual: true, virtualConsole: vc, url: 'https://x.local/',
      beforeParse(w) {
        w.AudioContext = stubAudio(); w.webkitAudioContext = stubAudio();
        w.URL.createObjectURL = () => 'blob:t'; w.URL.revokeObjectURL = () => {};
        w.confirm = () => true;
      },
    });
    setTimeout(() => resolve(dom.window), 1200);
  });
}
const POOL_KEYS = ['spring', 'summer', 'autumn', 'winter', 'youthSpring', 'youthSummer', 'youthAutumn', 'youthWinter'];
let ID_TOPIC = {};   // 池事件 id → 题材（真实口径 ③ 用；后续段落在 STORY 里，不进池、不在 S.recent）
async function poolStats() {
  const win = await loadGame();
  const stats = JSON.parse(win.eval(`JSON.stringify((function(){
    const out={};const idTopic={};
    ${JSON.stringify(POOL_KEYS)}.forEach(function(k){
      const list=(POOLS[k]||[]);
      const cnt={drama:0,routine:0};const topics={};
      list.forEach(function(e){
        cnt[evKindOf(e)]=(cnt[evKindOf(e)]||0)+1;
        const tp=evTopicOf(e);topics[tp]=(topics[tp]||0)+1;
        idTopic[e.id]=tp;
      });
      out[k]={size:list.length,drama:cnt.drama||0,routine:cnt.routine||0,topics:topics};
    });
    out.__idTopic=idTopic;
    return out;
  })())`));
  ID_TOPIC = stats.__idTopic || {};
  delete stats.__idTopic;
  return stats;
}
function printPoolStats(stats) {
  console.log('\n══ ⑥ 四季池内容均衡（P2.2）══');
  for (const k of POOL_KEYS) {
    const v = stats[k];
    if (!v.size) { console.log('  ' + padR(k, 14) + ' （空池）'); continue; }
    const ratio = (v.drama / v.size * 100).toFixed(0) + '%';
    const tops = Object.entries(v.topics).sort((a, b) => b[1] - a[1]).slice(0, 4)
      .map(x => x[0] + '=' + x[1]).join(' ');
    console.log('  ' + padR(k, 14) + padL(v.size, 4) + ' 条 · 戏剧 ' + padR(ratio, 5) + ' · 题材：' + tops);
  }
  console.log('\n  → 戏剧占比低的池子，就是把总体比例拉低的地方（对照 EV_DRAMA_SHARE=.45）');
  return stats;
}

(async () => {
  const stats = await poolStats();          // 池统计 + id→题材映射（③ 真实口径依赖它）
  printPoolStats(stats);
  main();
  fs.writeFileSync(path.resolve(__dirname, 'sim_report.json'),
    JSON.stringify({ poolStats: stats }, null, 2));
})().catch(e => { console.error('分析失败：', e && (e.stack || e.message || e)); process.exit(1); });
