# -*- coding: utf-8 -*-
"""给 test_ai.js 追加「只输出正文」（v4.20.3）断言：规则注入 + 清洗兜底。"""
import io

P = 'test_ai.js'
s = io.open(P, encoding='utf-8').read()

block = """
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
    preamble: AI.san('好的，以下是战报：\\n10月下旬首个客场，勇士以140比108取胜。'),
    label: AI.san('草稿\\n10月下旬首个客场，勇士获胜。'),
    fence: AI.san('```\\n勇士以140比108取胜。\\n```'),
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
"""

# 插到最后一个 '});' 之前
idx = s.rstrip().rfind('});')
assert idx > 0, 'tail anchor not found'
s = s[:idx] + block + '\n' + s[idx:]
io.open(P, 'w', encoding='utf-8').write(s)
print('test_ai 已追加只输出正文断言')
