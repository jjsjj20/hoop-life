// 桌面探针：仅属性页通栏（v5.0.4）
const fs = require('fs'), path = require('path');
const { JSDOM } = require('jsdom');
const html = fs.readFileSync(path.join(__dirname, '篮球人生.html'), 'utf-8');
const dom = new JSDOM(html, { runScripts: 'dangerously', pretendToBeVisual: true,
  beforeParse(w) { w.matchMedia = () => ({ matches: true, media:'', addEventListener(){}, removeEventListener(){}, addListener(){}, removeListener(){} }); } });
const w = dom.window, d = w.document;
const errs = [];
w.addEventListener('error', e => errs.push(e.message));
let ok = 0, bad = 0;
const T = (name, cond) => { cond ? ok++ : bad++; console.log((cond ? '✓' : '✗') + ' ' + name); };

// 最小职业段玩家状态（let S 在页面全局词法环境，须用 w.eval 注入）
const KEYS = ['finish','dunk','three','mid','free','handle','pass','perdef','steal','intdef','block','reb','speed','strength','clutch'];
const sk = KEYS.map(k => k + ':60').join(',');
w.eval(`S={name:'林一飞',pos:'PG',league:'NBA',stage:'regular',day:100,season:1,h:{clutch:60},skills:{${sk}},a:{athBase:60},assets:[],cash:5000,wage:null,contract:null,grind:0,value:100,flags:{}}`);
w.eval('syncFromSkills()');
w.eval('UI={mode:"event",ev:null};renderGame()');

// 属性页
w.showAttrs();
T('属性页进入 #stage', !!d.querySelector('#stage .funcpage'));
T('属性页带 .attrswide 标记', !!d.querySelector('#stage .attrswide'));
w.closeOvl();

// 其他功能页（财务）
w.showMoney();
T('财务页进入 #stage', !!d.querySelector('#stage .funcpage'));
T('财务页不带 .attrswide', !d.querySelector('#stage .attrswide'));
w.closeOvl();

// 名单页
w.showRoster();
T('名单页不带 .attrswide', !d.querySelector('#stage .attrswide'));
w.closeOvl();

// CSS 断言
T('CSS: #stage 默认 760px', html.includes('#stage{max-width:760px;margin:0 auto}'));
T('CSS: attrswide 放开通栏', html.includes('#stage:has(.attrswide){max-width:none}'));
T('CSS: 旧 scene 规则已移除', !html.includes('#stage:has(.scene)'));
T('手机端不受影响（媒体查询内）', /@media\(min-width:900px\)\{[\s\S]*?#stage\{max-width:760px/.test(html));

T('无运行时错误', errs.length === 0);
if (errs.length) console.log('  错误:', errs.join(' | '));
console.log(`\n合计 ${ok} 通过 / ${bad} 失败`);
process.exit(bad ? 1 : 0);
