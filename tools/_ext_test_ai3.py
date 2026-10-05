# -*- coding: utf-8 -*-
"""给 test_ai.js 追加「回声判定收紧 + 报纸重试」（v4.20.5）断言。"""
import io

P = 'test_ai.js'
s = io.open(P, encoding='utf-8').read()

N = "String.fromCharCode(10)"
block = """
  const N = String.fromCharCode(10);

  // ── ⑩ 回声判定收紧（v4.20.5）：报纸正文不再被误判 ──
  const fp = JSON.parse(win.eval(`JSON.stringify({
    realPaper: AI.looksLikeEcho('【头版】勇士主场109比108险胜森林狼。' + ${N} + '【联盟风云】控卫打末节接管比赛。' + ${N} + '【流言板】据悉，更衣室人士透露……' + ${N} + '【宿敌口水】赛前双方隔空喊话。' + ${N} + '【新星追踪】新秀迎来首秀。'),
    twoLabels: AI.looksLikeEcho('结果：勇士取胜。球员：打，27分。'),
    oneWeak: AI.looksLikeEcho('这场比赛的结果很关键，要求很高。'),
    strong: AI.looksLikeEcho('只使用给定数据，不能编造其他球员姓名。'),
    threeLabels: AI.looksLikeEcho('球员：打' + ${N} + '比赛：揭幕战' + ${N} + '结果：109比108')
  })`));
  check('真实报纸正文不误判（含【】栏目与「据悉」）', fp.realPaper === false);
  check('只引 2 个事实标签不误判', fp.twoLabels === false, String(fp.twoLabels));
  check('弱特征单次出现不误判', fp.oneWeak === false, String(fp.oneWeak));
  check('强特征仍能识别回声', fp.strong === true);
  check('3 个事实标签判为回声', fp.threeLabels === true);

  // ── ⑪ 报纸：回声 → 重试一次 → 缓存干净正文 ──
  win.eval(`
    S.worldNews=['测试新闻一','测试新闻二','测试新闻三'];
    AI._ev=null;
    window.__reqs=[];
    window.__plan=[
      {choices:[{message:{content:'只使用给定素材，不能编造。球员：打 比赛：X 结果：Y'}}]},
      {choices:[{message:{content:'【头版】勇士主场取胜。' + String.fromCharCode(10) + '【联盟风云】他末节接管。' + String.fromCharCode(10) + '【流言板】据悉，更衣室人士透露。' + String.fromCharCode(10) + '【宿敌口水】隔空喊话。' + String.fromCharCode(10) + '【新星追踪】新秀首秀。'}}]}
    ];
    window.__el3=document.createElement('div');
    AI.newsGo(window.__el3);
  `);
  await new Promise(r => setTimeout(r, 80));
  const newsRes = JSON.parse(win.eval(`(function(){
    const b=AI.newsBrief();
    return JSON.stringify({reqN:window.__reqs.length, cached:(b&&AI.cGet(b.key)||{}).t||''});
  })()`));
  check('报纸回声触发重试（共两次请求）', newsRes.reqN === 2, String(newsRes.reqN));
  check('报纸缓存写入干净正文', newsRes.cached.indexOf('【头版】') >= 0 && newsRes.cached.indexOf('不能编造') < 0,
    newsRes.cached.slice(0, 24));

  // ── ⑫ 报纸连续回声 → 报错且不写缓存 ──
  win.eval(`
    window.__reqs=[];
    window.__plan=[
      {choices:[{message:{content:'不能编造其他球员姓名。球员：打 比赛：X 结果：Y'}}]},
      {choices:[{message:{content:'只使用给定素材。球员：打 比赛：X 结果：Y'}}]}
    ];
    window.__el4=document.createElement('div');
    AI.newsGo(window.__el4);
  `);
  await new Promise(r => setTimeout(r, 80));
  const newsFail = JSON.parse(win.eval(`(function(){
    const b=AI.newsBrief();
    return JSON.stringify({txt:window.__el4.textContent||'', cached:(b&&AI.cGet(b.key)||{}).t||''});
  })()`));
  check('报纸连续回声给明确提示', /复述|失败/.test(newsFail.txt), newsFail.txt.slice(0, 40));
  check('报纸连续回声不写缓存', newsFail.cached.indexOf('不能编造') < 0, newsFail.cached.slice(0, 20));
"""

idx = s.rstrip().rfind('});')
assert idx > 0, 'tail anchor not found'
s = s[:idx] + block + '\n' + s[idx:]
io.open(P, 'w', encoding='utf-8').write(s)
print('test_ai 已追加回声收紧与报纸重试断言')
