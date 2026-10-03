/* 生涯分享卡（v4.11 P3.2）—— 计划验收：
 * 「分享卡本身也要能被测试（用 jsdom 渲染后断言关键数字与 S 一致）」
 * 附带：自包含（零外部引用）、终章按钮存在、下载流程在 jsdom 下可执行 */
const { run } = require('./testkit');

module.exports = run('分享卡', ({ win, doc, check }) => {
  win.eval('renderCreate();');
  win.eval("document.getElementById('fName').value='卡片先生';");
  win.eval('doCreate(); allocRandom(); confirmAlloc();');
  win.eval(`
    S.league='NBA';S.team='洛杉矶湖人';S.age=33;S.retired=true;S.pos='SG';
    S.career={seasons:10,pts:18600,reb:4200,ast:3600,stl:980,blk:520};
    S.history=[
      {y:'2016-17赛季',ppg:6.5},{y:'2017-18赛季',ppg:12.2},{y:'2018-19赛季',ppg:18.4},
      {y:'2019-20赛季',ppg:24.6},{y:'2020-21赛季',ppg:26.1},{y:'2021-22赛季',ppg:22.8},
      {y:'2022-23赛季',ppg:20.5},{y:'2023-24赛季',ppg:19.2},{y:'2024-25赛季',ppg:17.7},
      {y:'2025-26赛季',ppg:15.4}];
    S.played=['辽宁本钢','洛杉矶湖人'];
    S.honors=[{y:'2020-21赛季',t:'总冠军'},{y:'2020-21赛季',t:'常规赛MVP'},{y:'2022-23赛季',t:'全明星'}];
    S.peakO=91;S.assets=S.assets||[];S.fin=S.fin||{};ensureWorld();`);

  const html = win.eval('shareCardHTML()');

  // ── 关键数字与 S 一致 ─────────────────────────────
  const exp = {
    pts: Math.round(18600 / 10 * 10) / 10,   // 1860
    reb: Math.round(4200 / 10 * 10) / 10,    // 420
    ast: Math.round(3600 / 10 * 10) / 10,    // 360
    stl: Math.round(980 / 10 * 10) / 10,     // 98
    blk: Math.round(520 / 10 * 10) / 10      // 52
  };
  check('包含球员名', html.indexOf('卡片先生') >= 0);
  check('场均得分 = Σpts/Σseasons（' + exp.pts + '）', html.indexOf('>' + exp.pts + '<') >= 0, '期望 >' + exp.pts + '<');
  check('场均篮板一致（' + exp.reb + '）', html.indexOf('>' + exp.reb + '<') >= 0);
  check('场均助攻一致（' + exp.ast + '）', html.indexOf('>' + exp.ast + '<') >= 0);
  check('场均抢断一致（' + exp.stl + '）', html.indexOf('>' + exp.stl + '<') >= 0);
  check('场均盖帽一致（' + exp.blk + '）', html.indexOf('>' + exp.blk + '<') >= 0);
  check('最高 OVR 一致（91）', html.indexOf('>91<') >= 0);
  check('赛季数一致（10）', html.indexOf('>10 个赛季') >= 0 || html.indexOf('10 个赛季') >= 0);
  check('荣誉全部出现', ['总冠军', '常规赛MVP', '全明星'].every(t => html.indexOf(t) >= 0));
  check('效力球队路径出现', html.indexOf('辽宁本钢') >= 0 && html.indexOf('洛杉矶湖人') >= 0);
  check('生涯跨度与 birthYear 一致',
    html.indexOf(win.eval("'篮球生涯 '+(S.birthYear+15)+'–'+(S.birthYear+S.age)")) >= 0);

  // ── 形态：完整文档 + 内联 SVG 曲线 ──────────────────
  check('是完整 HTML 文档（DOCTYPE 到 </html>）',
    html.indexOf('<!DOCTYPE html>') === 0 && html.indexOf('</html>') > 0);
  check('得分曲线为内联 SVG 且每个赛季一个数据点',
    /<svg/.test(html) && (html.match(/<circle/g) || []).length === 10,
    'circles=' + (html.match(/<circle/g) || []).length);
  check('包含生涯评语', /<div class="quote">/.test(html));

  // ── 自包含：零外部引用 ───────────────────────────
  check('无 http(s) 外链', !/https?:\/\//.test(html));
  check('无本地 assets 引用', !/assets\//.test(html));
  check('无外链脚本/图片标签', !/<script/.test(html) && !/<img/.test(html));

  // ── 终章按钮与下载流程 ───────────────────────────
  win.eval('UI={mode:"end"};showEnd();');
  check('终章页有「生成分享卡」按钮',
    doc.getElementById('app').innerHTML.indexOf('生成分享卡') >= 0);
  const dl = win.eval('(function(){try{shareCardDL();return true;}catch(e){return "ERR:"+(e&&e.message||e);}})()');
  check('shareCardDL 在 jsdom 下可执行（Blob/URL/download 全链路）', dl === true, String(dl));
});
