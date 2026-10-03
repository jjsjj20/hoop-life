/* M1 调参前后对比：用合并口径（Σdrama/Σseen），避免少量超长生涯主导均值 */
const fs = require('fs');
const path = require('path');

function load(name) {
  const raw = JSON.parse(fs.readFileSync(path.resolve(__dirname, name), 'utf8'));
  const seasons = [];
  for (const c of raw) for (const s of c.seasons) seasons.push({ ...s, league: c.league, mode: c.mode });
  return { careers: raw, seasons };
}

function pooled(seasons, filter) {
  const ss = seasons.filter(filter);
  const seen = ss.reduce((a, s) => a + s.seen, 0);
  const drama = ss.reduce((a, s) => a + s.drama, 0);
  return { n: ss.length, seen, drama, share: seen ? (drama / seen * 100).toFixed(1) + '%' : '—' };
}

function dupShare(raw, seasons) {
  // 真实口径 ③ 需要题材映射；这里只对比「有重复 id 的赛季占比」不行——
  // 简化：复用 analyze 的结论，此处只算戏剧与数量。③ 由 analyze 输出。
  return seasons.length;
}

function repeatRate(careers) {
  let total = 0, rep = 0;
  for (const c of careers) {
    const byYear = new Map();
    for (const s of c.seasons) {
      if (s.evY == null) continue;
      if (!byYear.has(s.evY)) byYear.set(s.evY, new Set());
      const set = byYear.get(s.evY);
      for (const id of (s.ids || [])) set.add(id);
    }
    const years = [...byYear.keys()].sort((a, b) => a - b);
    for (let i = 0; i < years.length; i++) {
      for (const id of byYear.get(years[i])) {
        total++;
        for (let j = i - 1; j >= 0 && years[i] - years[j] <= 4; j--) {
          if (byYear.get(years[j]).has(id)) { rep++; break; }
        }
      }
    }
  }
  return { total, rep, rate: total ? (rep / total * 100).toFixed(1) + '%' : '—' };
}

const B = load('sim_raw_before.json');
const A = load('sim_raw_after.json');

const rows = [
  ['全部赛季（合并口径）', s => true],
  ['沉浸模式', s => s.mode === 'immersive'],
  ['NBA（沉浸）', s => s.mode === 'immersive' && s.league === 'NBA'],
  ['CBA（沉浸）', s => s.mode === 'immersive' && s.league === 'CBA'],
  ['欧洲（沉浸）', s => s.mode === 'immersive' && s.league === '欧洲'],
];

console.log('══ 戏剧占比：合并口径 Σdrama/Σseen ══');
console.log('  ' + '样本'.padEnd(16) + '  调整前              调整后');
for (const [label, f] of rows) {
  const b = pooled(B.seasons, f), a = pooled(A.seasons, f);
  const fmt = x => x.share + '（' + x.drama + '/' + x.seen + '）';
  console.log('  ' + label.padEnd(16) + '  ' + fmt(b).padEnd(20) + fmt(a));
}

const rb = repeatRate(B.careers), ra = repeatRate(A.careers);
console.log('\n══ ④ 4 年内重复率 ══');
console.log('  调整前 ' + rb.rate + '（' + rb.rep + '/' + rb.total + '）· 调整后 ' + ra.rate + '（' + ra.rep + '/' + ra.total + '）');

// 每季事件数（沉浸，合并中位）
const med = arr => { const a = arr.slice().sort((x, y) => x - y); return a.length ? a[Math.floor(a.length / 2)] : '—'; };
console.log('\n══ 每季事件数（沉浸，中位）══');
console.log('  调整前 ' + med(B.seasons.filter(s => s.mode === 'immersive').map(s => s.seen)) +
            ' · 调整后 ' + med(A.seasons.filter(s => s.mode === 'immersive').map(s => s.seen)));
