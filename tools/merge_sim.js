/* 把 sim_part_<i>.json 分片合并成 sim_raw.json（配合 sim_pacing.js 的 SIM_ONE 模式） */
const fs = require('fs');
const path = require('path');
const dir = __dirname;
const parts = fs.readdirSync(dir)
  .filter(f => /^sim_part_\d+\.json$/.test(f))
  .sort((a, b) => Number(a.match(/\d+/)[0]) - Number(b.match(/\d+/)[0]));
if (!parts.length) { console.error('没有找到 sim_part_*.json'); process.exit(1); }
const out = parts.map(f => JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8')));
fs.writeFileSync(path.join(dir, 'sim_raw.json'), JSON.stringify(out));
console.log('合并 ' + parts.length + ' 个分片 → sim_raw.json（共 ' +
  out.reduce((n, c) => n + c.seasons.length, 0) + ' 个赛季）');
