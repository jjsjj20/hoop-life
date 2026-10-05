/* AI 生成兼容性（v4.20.2）——回归钉：
 *  ① textOf 兼容四种响应形状（content 字符串 / 数组分片 / reasoning_content / choices[0].text）
 *  ② 默认预算 900、超时随预算放大
 *  ③ 空内容（思考吃光预算）→ 自动抬预算、去掉 json 重试一次并成功
 *  ④ 失败信息带 finish_reason，便于定位
 *  ⑤ san 支持自定义上限（报纸长文不再被 700 字截断） */
const { run } = require('./testkit');

module.exports = run('AI 生成兼容', async ({ win, check, html }) => {
  // ── ① textOf：四种响应形状 ──
  const shapes = JSON.parse(win.eval(`JSON.stringify({
    plain: AI.textOf({choices:[{message:{content:'一段战报'}}]}),
    parts: AI.textOf({choices:[{message:{content:[{type:'text',text:'上'},{type:'text',text:'半段'}]}}]}),
    reason: AI.textOf({choices:[{message:{content:'',reasoning_content:'思考型模型的正文'}}]}),
    legacy: AI.textOf({choices:[{text:'旧版 completions 形状'}]}),
    outText: AI.textOf({output_text:'output_text 形状'})
  })`));
  check('content 字符串', shapes.plain === '一段战报', shapes.plain);
  check('content 数组分片拼接', shapes.parts === '上半段', shapes.parts);
  check('reasoning_content 兜底', shapes.reason === '思考型模型的正文', shapes.reason);
  check('choices[0].text 兜底', shapes.legacy === '旧版 completions 形状', shapes.legacy);
  check('output_text 兜底', shapes.outText === 'output_text 形状', shapes.outText);

  // ── ⑤ san 自定义上限 ──
  const long = 'x'.repeat(1500);
  check('san 默认 700 上限', win.eval(`AI.san(${JSON.stringify(long)}).length`) === 700);
  check('san 可放宽到 1200（报纸长文）', win.eval(`AI.san(${JSON.stringify(long)},1200).length`) === 1200);

  // ── 打桩 fetch：按脚本返回 ──
  win.eval(`
    window.__reqs=[];
    window.__plan=[];
    window.fetch=function(url,init){
      window.__reqs.push(JSON.parse(init.body));
      const r=window.__plan.shift();
      return Promise.resolve({ok:true,status:200,json:function(){return Promise.resolve(r);}});
    };
    AI.cfg={on:true,url:'https://mock.local/v1',key:'k',model:'mock-model'};
  `);

  // ── ② 默认预算 900 ──
  win.eval(`window.__plan=[{choices:[{message:{content:'默认预算的正文'},finish_reason:'stop'}]}];`);
  const t1 = await win.eval('AI.ask("sys","user")');
  const req1 = JSON.parse(win.eval('JSON.stringify(window.__reqs[0])'));
  check('成功路径返回正文', t1 === '默认预算的正文', t1);
  check('默认 max_tokens = 900（原 360）', req1.max_tokens === 900, String(req1.max_tokens));

  // ── ③ 空内容 → 抬预算重试 ──
  win.eval(`
    window.__reqs=[];
    window.__plan=[
      {choices:[{message:{content:''},finish_reason:'length'}]},
      {choices:[{message:{content:'重试后的正文'}}]}
    ];
  `);
  const t2 = await win.eval('AI.ask("sys","user",{mt:800,json:true})');
  const reqs2 = JSON.parse(win.eval('JSON.stringify(window.__reqs)'));
  check('空内容后自动重试并成功', t2 === '重试后的正文', t2);
  check('重试共发两次请求', reqs2.length === 2, String(reqs2.length));
  check('重试抬大预算（≥1200）', reqs2[1].max_tokens >= 1200, String(reqs2[1].max_tokens));
  check('重试去掉 response_format', reqs2[1].response_format === undefined, JSON.stringify(reqs2[1].response_format));

  // ── ④ 两次都空 → 错误信息带 finish_reason ──
  win.eval(`
    window.__reqs=[];
    window.__plan=[
      {choices:[{message:{content:''},finish_reason:'length'}]},
      {choices:[{message:{content:''},finish_reason:'length'}]}
    ];
  `);
  let errMsg = '';
  try { await win.eval('AI.ask("sys","user")'); } catch (e) { errMsg = String(e && e.message || e); }
  check('失败信息含 finish_reason', errMsg.indexOf('finish_reason=length') >= 0, errMsg);

  // ── ⑦ 只输出正文：系统提示词统一带规则 ──
  check('文本类请求的系统提示词带「只输出正文」规则',
    html.indexOf('只输出正文本身') >= 0 && html.indexOf('AI.RULE_ONLY=') >= 0);
  check('JSON 类请求用专用规则', html.indexOf('只输出一个 JSON 对象本身') >= 0);
  win.eval(`
    window.__reqs=[];
    window.__plan=[{choices:[{message:{content:'正文'}}]}];
  `);
  await win.eval('AI.ask("你是解说员","写战报")');
  const sysTxt = JSON.parse(win.eval('JSON.stringify(window.__reqs[0].messages[0].content)'));
  check('实际请求里规则已拼进 system', sysTxt.indexOf('只输出正文本身') >= 0, sysTxt.slice(-40));
  win.eval(`
    window.__reqs=[];
    window.__plan=[{choices:[{message:{content:'{"a":1}'}}]}];
  `);
  await win.eval('AI.ask("sys","user",{json:true})');
  const sysJson = JSON.parse(win.eval('JSON.stringify(window.__reqs[0].messages[0].content)'));
  check('JSON 请求里带 JSON 专用规则', sysJson.indexOf('只输出一个 JSON 对象本身') >= 0, sysJson.slice(-30));

  // ── ⑧ 清洗兜底：模型不守规矩时也只留正文 ──
  const strip = JSON.parse(win.eval(`JSON.stringify({
    preamble: AI.san('好的，以下是战报：' + String.fromCharCode(10) + '10月下旬首个客场，勇士以140比108取胜。'),
    label: AI.san('草稿' + String.fromCharCode(10) + '10月下旬首个客场，勇士获胜。'),
    fence: AI.san(String.fromCharCode(96).repeat(3) + String.fromCharCode(10) + '勇士以140比108取胜。' + String.fromCharCode(10) + String.fromCharCode(96).repeat(3)),
    count: AI.san('勇士以140比108取胜。（约160字）'),
    quoted: AI.san('“勇士以140比108取胜。”'),
    keep: AI.san('这是一场属于老将的比赛。他出战42分钟。')
  })`));
  check('去掉开头寒暄行', strip.preamble === '10月下旬首个客场，勇士以140比108取胜。', strip.preamble);
  check('去掉行首「草稿」标签', strip.label === '10月下旬首个客场，勇士获胜。', strip.label);
  check('去掉代码围栏', strip.fence.indexOf('```') < 0 && strip.fence.indexOf('140比108') >= 0, strip.fence);
  check('去掉字数括注', strip.count === '勇士以140比108取胜。', strip.count);
  check('去掉整体包裹的引号', strip.quoted === '勇士以140比108取胜。', strip.quoted);
  check('正文首句不被误吃（含句号）', strip.keep.indexOf('这是一场属于老将的比赛。') === 0, strip.keep);


  // ── ⑨ 回声检测与重试（v4.20.4）──
  const echo = JSON.parse(win.eval(`JSON.stringify({
    instruction: AI.looksLikeEcho('要求：120-200字，不能编造其他球员姓名。'),
    labels: AI.looksLikeEcho('球员：打' + String.fromCharCode(10) + '比赛：揭幕战' + String.fromCharCode(10) + '结果：109比108'),
    normal: AI.looksLikeEcho('十月中，赛季揭幕战，金州勇士主场109比108险胜森林狼，34岁控卫打交出27分。')
  })`));
  check('识别指令复述为回声', echo.instruction === true);
  check('识别事实标签复述为回声', echo.labels === true);
  check('正常战报不误判', echo.normal === false);

  // 首次回声 → 带加强指令重试一次 → 缓存干净正文
  win.eval(`
    if(!S){renderCreate();document.getElementById('fName').value='AI测试';doCreate();allocRandom();confirmAlloc();S.league='NBA';S.team='金州勇士';S.age=34;S.pos='PG';ensureWorld();}
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

});
