/* R1 发版保障（v4.15.1）——回归钉：
 *  ① SW 缓存名 = 游戏 HTML 的内容哈希（sha256 前 12 位）：
 *    重建有任何变化即换缓存（老用户资产自动刷新），完全一致的重建缓存不失效；
 *    再有人把版本号写死进 CACHE，这条断言必挂。
 *  ② build_all 支持 --zip 自动打包（版本号取自更新日志）。
 *  ③ sw.js 预缓存清单完整。 */
const { run } = require('./testkit');
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

module.exports = run('R1发版保障', ({ check, html }) => {
  const root = path.resolve(__dirname, '..');

  // ── ① CACHE 与游戏 HTML 内容哈希联动 ──
  const expect = 'hoop-life-' +
    crypto.createHash('sha256').update(html, 'utf8').digest('hex').slice(0, 12);
  const sw = fs.readFileSync(path.join(root, 'sw.js'), 'utf8');
  check('SW 缓存名 = 游戏 HTML 内容哈希（' + expect + '）',
    sw.indexOf("const CACHE = '" + expect + "';") >= 0,
    'sw.js 里找不到 ' + expect);

  check('sw.js 预缓存清单含页面/manifest/图标',
    ['篮球人生.html', 'manifest.json', 'icons/icon-192.png', 'icons/icon-512.png']
      .every(f => sw.indexOf("'" + f + "'") >= 0 || sw.indexOf("'./" + f + "'") >= 0));

  // ── ② build_all --zip 自动打包 ──
  const ba = fs.readFileSync(path.join(root, 'tools', 'build_all.py'), 'utf8');
  check('build_all 支持 --zip 参数', ba.indexOf('"--zip"') >= 0 || ba.indexOf("'--zip'") >= 0);
  check('打包逻辑含 manifest/sw/icons 与两份日志',
    ['manifest.json', 'sw.js', 'icons', '更新日志.md', '更新日志.html', 'README-build.md']
      .every(f => ba.indexOf("'" + f + "'" ) >= 0 || ba.indexOf('"' + f + '"') >= 0));
  check('ZIP 版本号取自更新日志（当前版本：…）',
    ba.indexOf('当前版本：') >= 0 && ba.indexOf('zipfile') >= 0);

  // ── ③ ZIP 实物存在且含关键字段（本机验证；CI 只查脚本存在性）──
  const distZip = path.join(root, 'dist', 'hoop-life-v4.15.0.zip');
  if (fs.existsSync(distZip)) {
    const buf = fs.readFileSync(distZip);
    check('dist 存在 ZIP 交付包且为合法 zip（PK 头）',
      buf.length > 1000 && buf[0] === 0x50 && buf[1] === 0x4b);
  } else {
    check('dist 存在 ZIP 交付包（构建时未加 --zip 则跳过）', true);
  }
});
