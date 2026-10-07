/* 真实签位系统 —— 脚手架见 ./testkit.js */
const path = require('path');
const { run } = require('./testkit');

module.exports = run('真实签位系统', ({ win, doc, check, errors, warns, html }) => {
  win.eval('renderCreate();');
  doc.querySelector('#fName').value = '测试';
  win.eval('doCreate(); allocRandom(); confirmAlloc();');

  const nbaTeams = win.eval('TEAMS.nba.map(t=>t[0])');
  const cbaTeams = win.eval('TEAMS.cba.map(t=>t[0])');
  const isAsc = a => a.every((v, i) => i === 0 || a[i - 1] <= v);

  // ══ 结构：NBA ══
  // 战绩表与签位表必须在同一次求值里取——computeStandings 只缓存一个联赛，
  // 中间插一次别的联赛就会把 nba 战绩重新摇一遍，快照就对不上了。
  const snapN = JSON.parse(win.eval(`JSON.stringify((function(){
    const w={};computeStandings('nba').forEach(r=>{w[r.team]=r.wins;});
    return {wins:w, m:draftOrderOf('nba')};
  })())`));
  const WINS = snapN.wins, m = snapN.m;
  const wOf = t => WINS[t];
  check('NBA 签位表 = 全部 30 队的一个排列',
    m.order.length === 30 && new Set(m.order).size === 30 && nbaTeams.every(t => m.order.includes(t)));
  check('NBA 乐透区 14 队 · 只抽 4 签', m.lotto.length === 14 && m.draw.length === 4, m.lotto.length + '/' + m.draw.length);
  check('前 4 签全部来自乐透区', m.draw.every(d => m.lotto.includes(d.team)));
  const lotW = m.lotto.map(wOf), othW = m.order.filter(t => !m.lotto.includes(t)).map(wOf);
  check('乐透区 = 战绩最差的 14 队（并列按抽签顺序）', Math.max(...lotW) <= Math.min(...othW),
    '乐透最差 ' + Math.max(...lotW) + ' vs 非乐透最好 ' + Math.min(...othW));
  check('5-14 签：剩下的 10 支乐透队 · 按战绩倒序', m.order.slice(4, 14).length === 10 &&
    m.order.slice(4, 14).every(t => m.lotto.includes(t)) && !m.draw.some(d => m.order.slice(4, 14).includes(d.team)) &&
    isAsc(m.order.slice(4, 14).map(wOf)));
  check('15-30 签：16 支季后赛球队 · 按战绩倒序', m.order.slice(14).length === 16 &&
    m.order.slice(14).every(t => !m.lotto.includes(t)) && isAsc(m.order.slice(14).map(wOf)));
  check('第 5 顺位起整体战绩不倒挂（4→29 单调）', isAsc(m.order.slice(4).map(wOf)));
  check('中签队都带上了状元签概率', m.draw.every(d => typeof d.p === 'number' && d.p > 0));

  // ══ 结构：CBA ══
  const snapC = JSON.parse(win.eval(`JSON.stringify((function(){
    const w={};computeStandings('cba').forEach(r=>{w[r.team]=r.wins;});
    return {wins:w, c:draftOrderOf('cba')};
  })())`));
  const CWINS = snapC.wins, c = snapC.c;
  check('CBA 签位表 = 全部 20 队的一个排列',
    c.order.length === 20 && new Set(c.order).size === 20 && cbaTeams.every(t => c.order.includes(t)));
  check('CBA 乐透区 8 队 · 只抽前 3 签', c.lotto.length === 8 && c.draw.length === 3, c.lotto.length + '/' + c.draw.length);
  check('前 3 签全部来自乐透区', c.draw.every(d => c.lotto.includes(d.team)));
  const clW = c.lotto.map(t => CWINS[t]), coW = c.order.filter(t => !c.lotto.includes(t)).map(t => CWINS[t]);
  check('CBA 乐透区 = 战绩最差的 8 队', Math.max(...clW) <= Math.min(...coW));
  check('CBA 4-8 签：剩下的 5 支乐透队 · 按战绩倒序', c.order.slice(3, 8).length === 5 &&
    c.order.slice(3, 8).every(t => c.lotto.includes(t)) && isAsc(c.order.slice(3, 8).map(t => CWINS[t])));
  check('CBA 9-20 签：12 支季后赛球队 · 按战绩倒序', c.order.slice(8).length === 12 &&
    isAsc(c.order.slice(8).map(t => CWINS[t])));
  check('抽签文案可读', /状元签 .+（.+%）/.test(win.eval('lottoText(draftOrderOf("nba").draw,draftOrderOf("nba").slot)')));

  // ══ 概率：蒙特卡洛（按每次实际分配到的赔率累计期望，避开并列扰动）══
  const N = 20000;
  win.eval('draftOrderOf("nba");');   /* 预热：把 nba 战绩固定进缓存，之后 2 万次用同一张表 */
  win.eval(`
    (function(){
      const N=${N},F={},E={};
      for(let k=0;k<N;k++){
        const r=draftOrderOf('nba');
        if(r.order.length!==30||new Set(r.order).size!==30){window.__bad=(window.__bad||0)+1;}
        const w=r.draw[0].team;F[w]=(F[w]||0)+1;
        r.lotto.forEach(function(t,i){E[t]=(E[t]||0)+((NBA_LOTTO_ODDS[i]||0)/100/N);});
      }
      window.__freq=F;window.__exp=E;
    })();
  `);
  const F = win.eval('window.__freq'), E = win.eval('window.__exp');
  const t0 = Date.now();
  win.eval('for(let i=0;i<5000;i++)draftOrderOf("nba");');
  const per = (Date.now() - t0) / 5000;
  check('2 万次抽签都是合法排列', (win.eval('window.__bad') || 0) === 0);
  check('单次抽签耗时 < 1ms', per < 1, per.toFixed(3) + 'ms');

  const teams = Object.keys(E);
  const errs = teams.map(t => ({ t, exp: E[t], got: (F[t] || 0) / N, d: Math.abs((F[t] || 0) / N - E[t]) }));
  const maxErr = Math.max(...errs.map(x => x.d));
  check('每队状元签概率贴合官方赔率（偏差 < 1%）', maxErr < 0.01, '最大偏差 ' + (maxErr * 100).toFixed(2) + '%');
  check('期望总概率 = 100%（14 队瓜分状元签）', Math.abs(teams.reduce((s, t) => s + E[t], 0) - 1) < 1e-6);

  const sorted = errs.slice().sort((a, b) => b.exp - a.exp);
  check('最差 3 队期望中签率各约 13-14%', sorted.slice(0, 3).every(x => x.exp > 0.12 && x.exp < 0.15),
    sorted.slice(0, 3).map(x => x.t + '=' + (x.exp * 100).toFixed(2) + '%').join(' '));
  check('乐透末位期望中签率 < 1%', sorted[sorted.length - 1].exp < 0.01,
    (sorted[sorted.length - 1].exp * 100).toFixed(2) + '%');
  check('不是等概率：首位期望 ≥ 末位 10 倍',
    sorted[0].exp >= sorted[sorted.length - 1].exp * 10,
    (sorted[0].exp * 100).toFixed(2) + '% vs ' + (sorted[sorted.length - 1].exp * 100).toFixed(2) + '%');

  // 抽签确实会改变前 4 签（不是照抄战绩倒序）
  let moved = 0;
  for (let k = 0; k < 300; k++) {
    const r = JSON.parse(win.eval('JSON.stringify(draftOrderOf("nba"))'));
    const rec = r.order.filter(t => r.lotto.includes(t)).sort((a, b) => wOf(a) - wOf(b)).slice(0, 4);
    if (r.order.slice(0, 4).join() !== rec.join()) moved++;
  }
  check('抽签真的会改变前 4 签顺序（不是照抄战绩）', moved > 150, '300 次里 ' + moved + ' 次发生移位');

  console.log('  状元签期望 vs 实测（按期望排序，前 6）：');
  sorted.slice(0, 6).forEach(x =>
    console.log('    %s  期望 %s%%  实测 %s%%', x.t.padEnd(8), (x.exp * 100).toFixed(2), (x.got * 100).toFixed(2)));

  // ══ 端到端：抽签呈现路径（v4.27.0 起改为「揭晓页逐位揭牌」，选秀夜不再剧透） ══
  const night = JSON.parse(win.eval('JSON.stringify(evDraftNight())'));
  check('选秀夜场景不再提前剧透抽签结果', !/本届乐透抽签/.test(night.scene), (night.scene || '').slice(0, 60));
  const lottoTxt = win.eval('lottoText(ensureDraft().draw,ensureDraft().slot)');
  check('抽签文案仍有状元签归属与概率（揭晓页/播报同源）', /状元签 .+（\d/.test(String(lottoTxt)), String(lottoTxt).slice(0, 60));
  const combine = JSON.parse(win.eval('JSON.stringify(evDraftCombine())'));
  check('联合试训场景仍正常（未受改动影响）', /选前行情/.test(combine.scene));

}, { ready: 1200 });
