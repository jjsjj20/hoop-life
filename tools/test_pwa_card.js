/* P8 分享卡图片版 + P6 PWA（v4.15）——回归钉：
 *  ① shareCardData() 数据模型与 S 一致（计划验收：分享卡可测试）
 *  ② drawShareCard 用录制式 ctx 断言关键数字真的被画出来（无需 canvas 原生包）
 *  ③ shareCardPNG 全链路：toBlob→下载；无画布环境自动回退网页版
 *  ④ PWA：manifest 合法、SW 缓存策略齐全、图标存在、注册带协议守卫、AI 离线明示降级 */
const { run } = require('./testkit');
const fs = require('fs');
const path = require('path');

module.exports = run('PWA与图片分享卡', ({ win, doc, check, html }) => {
  win.eval('renderCreate();');
  win.eval("document.getElementById('fName').value='卡片的影子';");
  win.eval('doCreate(); allocRandom(); confirmAlloc();');
  win.eval(`
    S.league='NBA'; S.team='洛杉矶湖人'; S.age=33; S.retired=true; S.pos='SG';
    S.career={seasons:10,pts:18600,reb:4200,ast:3600,stl:980,blk:520};
    S.history=[
      {y:'2016-17赛季',ppg:6.5},{y:'2017-18赛季',ppg:12.2},{y:'2018-19赛季',ppg:18.4},
      {y:'2019-20赛季',ppg:24.6},{y:'2020-21赛季',ppg:26.1},{y:'2021-22赛季',ppg:22.8},
      {y:'2022-23赛季',ppg:20.5},{y:'2023-24赛季',ppg:19.2},{y:'2024-25赛季',ppg:17.7},
      {y:'2025-26赛季',ppg:15.4}];
    S.played=['辽宁本钢','洛杉矶湖人'];
    S.honors=[{y:'x',t:'总冠军'},{y:'x',t:'常规赛MVP'}];
    S.peakO=91;S.assets=S.assets||[];S.fin=S.fin||{};ensureWorld();
  `);

  // ── ① 数据模型与 S 一致 ──
  const d = JSON.parse(win.eval('JSON.stringify(shareCardData())'));
  const exp = {pts:'1860',reb:'420',ast:'360',stl:'98',blk:'52'};
  check('数据模型包含球员名', d.name === '卡片的影子', d.name);
  check('场均五项与 S 一致', String(d.stats.pts) === exp.pts && String(d.stats.reb) === exp.reb && String(d.stats.ast) === exp.ast && String(d.stats.stl) === exp.stl && String(d.stats.blk) === exp.blk, JSON.stringify(d.stats));
  check('最高 OVR / 赛季数 / 荣誉数一致', d.peak === 91 && d.seasons === 10 && d.honorsN === 2, JSON.stringify({peak:d.peak,seasons:d.seasons,honorsN:d.honorsN}));
  check('球队路径与曲线行一致', d.teams.join('|') === '辽宁本钢|洛杉矶湖人' && d.rows.length === 10, JSON.stringify(d.teams));

  // ── ② 录制式画布：关键数字真的被绘制 ──
  const REC = {texts:[]};
  const fakeCtx = new Proxy({}, {
    get(t, k){
      if(k === 'measureText') return txt => ({width: String(txt).length * 12});
      if(k === 'createLinearGradient') return () => ({addColorStop(){}});
      if(k === 'fillText') return (txt) => REC.texts.push(String(txt));
      return (typeof k === 'string' && k.slice(0,2) !== 'on') ? function(){} : undefined;
    },
    set(){ return true; }
  });
  const origCE = doc.createElement.bind(doc);
  doc.createElement = tag => tag === 'canvas' ? {width:0,height:0,getContext:()=>fakeCtx,toBlob:(cb)=>cb({size:1,type:'image/png'})} : origCE(tag);
  const pngRet = win.eval('shareCardPNG()');
  check('PNG 链路走通（toBlob→下载，返回 png）', pngRet === 'png', String(pngRet));
  check('画布绘出球员名与场均得分', REC.texts.some(t => t.indexOf('卡片的影子') >= 0) && REC.texts.some(t => t === exp.pts), JSON.stringify(REC.texts.slice(0, 8)));
  check('画布绘出荣誉与页脚', REC.texts.some(t => t.indexOf('总冠军') >= 0) && REC.texts.some(t => t.indexOf('图片分享卡') >= 0));
  // ── ③ 无画布环境回退网页版 ──
  doc.createElement = tag => tag === 'canvas' ? {width:0,height:0,getContext:()=>null} : origCE(tag);
  const fb = win.eval('shareCardPNG()');
  check('无画布环境自动回退网页版（返回 html，不抛错）', fb === 'html', String(fb));
  doc.createElement = origCE;

  // ── ④ PWA：manifest / sw / 图标 / 注册守卫 / AI 离线降级 ──
  const root = path.resolve(__dirname, '..');
  check('manifest.json 存在于仓库根', fs.existsSync(path.join(root, 'manifest.json')));
  const mf = JSON.parse(fs.readFileSync(path.join(root, 'manifest.json'), 'utf8'));
  check('manifest 关键字段齐全', mf.name && mf.start_url === './篮球人生.html' && mf.display === 'standalone' && Array.isArray(mf.icons) && mf.icons.length === 2, JSON.stringify(mf.icons || null));
  check('图标文件存在且非空（192/512）', ['icons/icon-192.png', 'icons/icon-512.png'].every(f => { const p = path.join(root, f); return fs.existsSync(p) && fs.statSync(p).size > 500; }));
  const sw = fs.readFileSync(path.join(root, 'sw.js'), 'utf8');
  check('sw.js 含版本化缓存常量', /const CACHE = 'hoop-life-v/.test(sw));
  check('sw.js 页面请求网络优先（navigate）', sw.indexOf("req.mode === 'navigate'") >= 0);
  check('sw.js 资产缓存优先且清理旧缓存', sw.indexOf('caches.match(req)') >= 0 && sw.indexOf('caches.delete') >= 0);
  check('sw.js 不拦截跨域请求（AI 接口）', sw.indexOf('origin !== location.origin') >= 0);
  check('HTML 含 manifest 链接', html.indexOf('rel="manifest" href="./manifest.json"') >= 0);
  check('SW 注册带协议守卫（file:// 不注册）', html.indexOf("/^https?:$/.test(location.protocol)") >= 0);
  check('AI 离线明示降级提示就位', html.indexOf('当前离线：AI 功能暂不可用') >= 0 && html.indexOf('navigator.onLine===false') >= 0);
  check('终章页有两个分享卡按钮（HTML+PNG）', html.indexOf('onclick="shareCardDL()"') >= 0 && html.indexOf('onclick="shareCardPNG()"') >= 0);
});