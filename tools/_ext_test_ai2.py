# -*- coding: utf-8 -*-
"""给 test_ai.js 追加「回声检测与重试」（v4.20.4）断言。"""
import io

P = 'test_ai.js'
s = io.open(P, encoding='utf-8').read()

block = """
  // ── ⑨ 回声检测与重试（v4.20.4）──
  const echo = JSON.parse(win.eval(`JSON.stringify({
    instruction: AI.looksLikeEcho('要求：120-200字，不能编造其他球员姓名。'),
    labels: AI.looksLikeEcho('球员：打\\n比赛：揭幕战\\n结果：109比108'),
    normal: AI.looksLikeEcho('十月中，赛季揭幕战，金州勇士主场109比108险胜森林狼，34岁控卫打交出27分。')
  })`));
  check('识别指令复述为回声', echo.instruction === true);
  check('识别事实标签复述为回声', echo.labels === true);
  check('正常战报不误判', echo.normal === false);

  // 首次回声 → 带加强指令重试一次 → 缓存干净正文
  win.eval(`
    S.gameLog=[];
    UI={mode:'result',ev:{id:'g1',title:'揭幕战',game:{name:'揭幕战',opp:'明尼苏达森林狼',home:true,res:{win:true,us:109,them:108,margin:1,box:{pts:27,reb:8,ast:13,stl:2,fga:23,fgm:9,tpa:9,tpm:3,fta:8,ftm:6,min:42},quarter:[7,5,7,8],clutch:true}}}};
    AI._kind='focus';
    AI.cfg={on:true,url:'https://mock.local/v1',key:'k',model:'mock-model'};
    window.__reqs=[];
    window.__plan=[
      {choices:[{message:{content:'要求：120-200字，不能编造其他球员姓名。球员：打 比赛：揭幕战'}}]},
      {choices:[{message:{content:'十月中，赛季揭幕战，金州勇士主场109比108险胜森林狼，34岁的控卫打末节接管比赛。'}}]}
    ];
    window.__el=document.createElement('div');
    AI.go(window.__el);
  `);
  await new Promise(r => setTimeout(r, 80));
  const keyM = JSON.parse(win.eval(`(function(){
    const b=AI.brief('focus');
    return JSON.stringify({k:AI.hash('focus|'+b.key), reqN:window.__reqs.length,
      cached:(AI.cGet(AI.hash('focus|'+b.key))||{}).t||''});
  })()`));
  check('回声触发重试（共两次请求）', keyM.reqN === 2, String(keyM.reqN));
  check('重试用加强指令（提示词含「再次强调」）',
    JSON.parse(win.eval('JSON.stringify(window.__reqs[1].messages[1].content)')).indexOf('再次强调') >= 0);
  check('缓存写入的是干净正文（非回声）',
    keyM.cached.indexOf('十月中') >= 0 && keyM.cached.indexOf('要求：') < 0, keyM.cached.slice(0, 30));

  // 连续回声 → 明确报错且不写缓存
  win.eval(`
    AI._kind='focus';
    window.__reqs=[];
    window.__plan=[
      {choices:[{message:{content:'要求：写一段战报。球员：打 结果：109比108'}}]},
      {choices:[{message:{content:'不能编造其他球员姓名。球员：打 比赛：揭幕战'}}]}
    ];
    window.__el2=document.createElement('div');
    AI.go(window.__el2);
  `);
  await new Promise(r => setTimeout(r, 80));
  const echoFail = JSON.parse(win.eval(`(function(){
    const b=AI.brief('focus');
    return JSON.stringify({txt:window.__el2.textContent||'', cached:(AI.cGet(AI.hash('focus|'+b.key))||{}).t||''});
  })()`));
  check('连续回声给出明确失败提示', echoFail.txt.indexOf('复述') >= 0, echoFail.txt.slice(0, 40));
  check('连续回声不写缓存（避免垃圾长期复现）', echoFail.cached.indexOf('要求') < 0, echoFail.cached.slice(0, 20));
"""

idx = s.rstrip().rfind('});')
assert idx > 0, 'tail anchor not found'
s = s[:idx] + block + '\n' + s[idx:]
io.open(P, 'w', encoding='utf-8').write(s)
print('test_ai 已追加回声检测断言')
