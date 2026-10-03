/* 一次跑完所有验证：9 个测试脚本 + AST 静态审查
 *
 * 本地和 CI 跑同一件事：node tools/verify_all.js
 *
 * 设计取舍：**同进程顺序执行**，不 spawn 子进程。
 *   · 子进程方案在本机被沙箱拦死（连 cmd.exe 都起不来），本地没法验证汇总逻辑本身；
 *   · 同进程更简单、更快，本地与 CI 行为完全一致。
 * 代价是某个测试卡住会拖住整轮——所以测试体抛错会被 testkit 转成一条失败断言，而不是崩掉汇总。
 */
/* 预检：jsdom 加载失败时给一句人话，而不是十屏「加载/执行失败」。
 * 真实踩过的报错：webidl.util.markAsUncloneable is not a function
 *   → Node 过旧（markAsUncloneable 要 Node ≥ 22.10）或装到了 jsdom 30（它带 undici 8）。
 * 所以这里把 jsdom 锁在 26.1.0（兼容 Node ≥ 18）。 */
try {
  require('jsdom');
} catch (e) {
  console.error('测试依赖 jsdom 加载失败：' + e.message);
  console.error('');
  console.error('两种常见原因：');
  console.error('  1) 还没装依赖 → 在仓库根跑 npm install');
  console.error('  2) Node 版本过旧 → jsdom 已锁 26.1.0（Node ≥ 18 即可）；若 package.json 里的 jsdom 被改成 30.x，请改回来');
  process.exit(2);
}

process.env.TESTKIT_COLLECT = '1';

const fs = require('fs');
const path = require('path');

const DIR = __dirname;
const files = fs.readdirSync(DIR).filter(f => /^test_.*\.js$/.test(f)).sort();
const jobs = files.map(f => ({ name: f, load: () => require(path.join(DIR, f)) }));
jobs.push({ name: 'audit.js', load: () => require(path.join(DIR, 'audit.js')) });

(async () => {
  const rows = [];
  let failed = 0;
  const t0 = Date.now();

  for (const job of jobs) {
    const label = job.name.replace(/\.js$/, '').replace(/^test_/, '');
    process.stdout.write('\n──── ' + label + ' ────\n');
    let r = null;
    try {
      r = await job.load();
    } catch (e) {
      r = { name: label, ok: false, line: '加载/执行失败: ' + ((e && e.message) || e) };
    }
    if (!r) r = { name: label, ok: false, line: '没有返回结果（忘了导出？）' };
    if (!r.ok) failed++;
    rows.push({ label, ok: r.ok, line: r.line || '', passed: r.passed, total: r.total });
  }

  const sum = k => rows.reduce((a, r) => a + (typeof r[k] === 'number' ? r[k] : 0), 0);
  const W = 62;
  console.log('\n╔' + '═'.repeat(W) + '╗');
  console.log('║ 篮球人生 · 验证汇总');
  console.log('╠' + '═'.repeat(W) + '╣');
  for (const r of rows) {
    console.log('║ ' + (r.ok ? '✓' : '✗') + ' ' + r.label.padEnd(18) + (r.line || '').padEnd(W - 22) + '║');
  }
  console.log('╠' + '═'.repeat(W) + '╣');
  console.log('║ 合计 ' + (rows.length - failed) + '/' + rows.length + ' 项通过 · 断言 ' +
    sum('passed') + '/' + sum('total') + ' · ' + ((Date.now() - t0) / 1000).toFixed(1) + ' 秒');
  console.log('╚' + '═'.repeat(W) + '╝');

  console.log(failed ? '\n有 ' + failed + ' 项未通过 —— 不要提交（CI 也会因此变红）。'
                     : '\n全部通过。可以提交了。');
  process.exit(failed ? 1 : 0);
})();
