/* 更新日志页面 —— 脚手架见 ./testkit.js */
const path = require('path');
const { run } = require('./testkit');

module.exports = run('更新日志页面', ({ win, doc, check, errors, warns, html }) => {
  // ── 1. 脚本无异常 ─────────────────────────────────
  check('页面脚本无未捕获异常', errors.length === 0, errors.slice(0, 3).join(' | '));

  // ── 2. 版本段落被正确切分与归类 ─────────────────────
  const secs = [...doc.querySelectorAll('section.ver')];
  check('版本段被包进 section.ver', secs.length === 47, '实得 ' + secs.length);
  check('总览/附录没有被误判成版本段', secs.every(s => /^sec-v/.test(s.id)));

  const kindOf = s => s.getAttribute('data-kind');
  const noOf = s => (s.querySelector('.vpill').textContent.match(/v[\d.]+/) || [''])[0];
  const kinds = secs.map(kindOf);
  check('每个版本段都有类型', kinds.every(k => k && k !== ''));
  const tally = kinds.reduce((a, k) => (a[k] = (a[k] || 0) + 1, a), {});
  check('类型分布合理（不是全归一类）', Object.keys(tally).length >= 3, JSON.stringify(tally));
  const kOf = no => { const x = secs.find(s => noOf(s) === no); return x ? kindOf(x) : '(未找到)'; };
  check('v4.7（剧情场景插画）→ 美术', kOf('v4.7') === 'art', kOf('v4.7'));
  check('v4.5（难度调整）→ 玩法', kOf('v4.5') === 'play', kOf('v4.5'));
  check('v4.6（稳定性优化）→ 修复', kOf('v4.6') === 'fix', kOf('v4.6'));
  check('v4.9（资源外置化）→ 工程', kOf('v4.9') === 'eng', kOf('v4.9'));
  check('v4.4（球队队徽）→ 美术', kOf('v4.4') === 'art', kOf('v4.4'));
  check('v4.9.5（代码审查）→ 工程', kOf('v4.9.5') === 'eng', kOf('v4.9.5'));
  check('v4.9.6（节奏复核）→ 玩法', kOf('v4.9.6') === 'play', kOf('v4.9.6'));
  check('v4.10.0（移除教练模式）→ 工程', kOf('v4.10.0') === 'eng', kOf('v4.10.0'));
  check('v4.11.0（签位交易+分享卡）→ 玩法', kOf('v4.11.0') === 'play', kOf('v4.11.0'));
  check('v4.12.0（收尾清零）→ 玩法', kOf('v4.12.0') === 'play', kOf('v4.12.0'));
  check('v4.13.0（内容补给）→ 玩法', kOf('v4.13.0') === 'play', kOf('v4.13.0'));
  check('v4.14.0（签位延伸）→ 玩法', kOf('v4.14.0') === 'play', kOf('v4.14.0'));
  check('v4.15.0（PWA+图片卡）→ 美术（图片版+图标）', kOf('v4.15.0') === 'art', kOf('v4.15.0'));
  check('v4.15.1（发版保障修复）→ 修复', kOf('v4.15.1') === 'fix', kOf('v4.15.1'));
  check('v4.16.0（摆烂机制·签位联动）→ 玩法', kOf('v4.16.0') === 'play', kOf('v4.16.0'));
  check('v4.17.0（青训补强）→ 玩法', kOf('v4.17.0') === 'play', kOf('v4.17.0'));
  check('v4.18.0（UI 减负）→ 工程', kOf('v4.18.0') === 'eng', kOf('v4.18.0'));
  check('v4.19.0（移动端布局重构）→ 工程', kOf('v4.19.0') === 'eng', kOf('v4.19.0'));
  check('v4.19.1（继续吸底修复）→ 修复', kOf('v4.19.1') === 'fix', kOf('v4.19.1'));
  check('v4.19.2（剧情折叠修复）→ 修复', kOf('v4.19.2') === 'fix', kOf('v4.19.2'));
  check('v4.20.0（难度重构）→ 玩法', kOf('v4.20.0') === 'play', kOf('v4.20.0'));
  check('v4.20.1（产出对齐）→ 玩法', kOf('v4.20.1') === 'play', kOf('v4.20.1'));
  check('v4.20.2（AI 修复）→ 修复', kOf('v4.20.2') === 'fix', kOf('v4.20.2'));
  check('v4.20.3（AI 只输出正文）→ 修复', kOf('v4.20.3') === 'fix', kOf('v4.20.3'));
  check('v4.20.4（AI 回声检测）→ 修复', kOf('v4.20.4') === 'fix', kOf('v4.20.4'));
  check('v4.20.5（回声判定收紧）→ 修复', kOf('v4.20.5') === 'fix', kOf('v4.20.5'));
  check('v4.21.0（AI 层移除）→ 工程', kOf('v4.21.0') === 'eng', kOf('v4.21.0'));
  check('v3.3（世界体育报·纯叙事层）→ 其他', kOf('v3.3') === 'other', kOf('v3.3'));
  check('v3.2（联赛校验修复）→ 修复', kOf('v3.2') === 'fix', kOf('v3.2'));
  check('v3.1（AI 致辞·纯叙事层）→ 其他', kOf('v3.1') === 'other', kOf('v3.1'));
  check('v3.5（视觉精修）→ 美术', kOf('v3.5') === 'art', kOf('v3.5'));
  check('v3.4（实时事件流）→ 玩法', kOf('v3.4') === 'play', kOf('v3.4'));

  // ── 3. 版本标题被拆成「徽章 + 主题」──────────────────
  const h = secs[0].querySelector('h2');
  check('版本标题有徽章元素', !!h.querySelector('.vpill'));
  check('徽章文字含版本号', /v4\.21\.0/.test(h.querySelector('.vpill').textContent), h.querySelector('.vpill').textContent);
  const vt = (h.querySelector('.vt') || {}).textContent || '';
  check('主题文字已从版本号里拆出来', vt.length > 6 && vt.indexOf('v4.21.0') < 0, JSON.stringify(vt.slice(0, 30)));
  check('提交哈希仍在标题里', /[0-9a-f]{7}/.test((h.querySelector('.sha') || {}).textContent || ''));

  // ── 4. 总览表：类型圆点 / 量级条 / 移动端 data-label ──
  const ov = doc.querySelector('.ovtable');
  const rows = [...ov.querySelectorAll('tr')].filter(r => r.querySelector('td'));
  check('总览表行数与版本段一致', rows.length === secs.length, rows.length + ' vs ' + secs.length);
  check('每行都有类型圆点', rows.every(r => r.querySelector('.dot')));
  check('圆点类型与段落一致', rows.every(r => {
    const no = r.querySelector('td').textContent.trim();
    const s = secs.find(x => noOf(x) === no);
    return s && r.querySelector('.dot').className === 'dot k-' + kindOf(s);
  }));
  check('字符增量列有量级条（±0 与补录条目无量级条属正常）', rows.filter(r => r.querySelector('.mg')).length >= rows.length - 3,
    rows.filter(r => r.querySelector('.mg')).length + '/' + rows.length);
  check('单元格带 data-label（窄屏卡片化用）',
    rows[0].querySelectorAll('td[data-label]').length >= 3);

  // ── 5. 工具条 ────────────────────────────────────
  const jump = doc.getElementById('tbJump');
  const chips = [...jump.querySelectorAll('a')];
  check('目录芯片被搬进工具条（47 版 + 附录）', chips.length === 48, String(chips.length));
  const verChips = chips.filter(a => /^#v\d/.test(a.getAttribute('href')));
  check('版本芯片都带上了类型色', verChips.length === 47 && verChips.every(a => /k-(art|play|eng|fix|other)/.test(a.className)),
    verChips.filter(a => !/k-/.test(a.className)).map(a => a.textContent).join(','));
  check('附录芯片保持中性（不属于任何版本类型）', /k-/.test((chips.find(a => /appendix/.test(a.getAttribute('href'))) || {}).className || '') === false);
  check('目录源标记仍在原位（只是运行时被搬走）', /<nav class="toc">/.test(html) && !doc.querySelector('header .toc'));

  const kindsBox = doc.getElementById('tbKinds');
  const kbtns = [...kindsBox.querySelectorAll('button')];
  check('类型筛选按钮已生成', kbtns.length >= 5, kbtns.map(b => b.textContent).join(' / '));
  check('筛选按钮带计数', /\d+/.test(kbtns[0].textContent), kbtns[0].textContent);
  check('默认选中「全部」', kbtns[0].getAttribute('aria-pressed') === 'true');

  // 点「美术」应只剩美术版本段
  const artBtn = kbtns.find(b => b.textContent.indexOf('美术') === 0);
  artBtn.dispatchEvent(new win.MouseEvent('click', { bubbles: true }));
  const visible = secs.filter(s => !s.classList.contains('hide'));
  check('筛选「美术」后只剩美术段', visible.length === tally.art && visible.every(s => kindOf(s) === 'art'),
    visible.length + '/' + tally.art);
  const visRows = rows.filter(r => !r.classList.contains('hide'));
  check('总览表同步筛选', visRows.length === visible.length, visRows.length + ' vs ' + visible.length);
  // 回到全部
  kbtns[0].dispatchEvent(new win.MouseEvent('click', { bubbles: true }));
  check('切回「全部」后恢复', secs.every(s => !s.classList.contains('hide')));

  // ── 6. 折叠 ──────────────────────────────────────
  const colBtn = doc.getElementById('tbCollapse');
  colBtn.dispatchEvent(new win.MouseEvent('click', { bubbles: true }));
  const collapsed = secs.filter(s => s.classList.contains('col'));
  check('「只看最近 5 版」收起后 5 个展开', collapsed.length === 47 - 5, String(collapsed.length));
  check('收起的是旧版本不是最新版', !secs.slice(0, 5).some(s => s.classList.contains('col')));
  check('按钮文字切换', colBtn.textContent.indexOf('展开全部') >= 0, colBtn.textContent);
  colBtn.dispatchEvent(new win.MouseEvent('click', { bubbles: true }));
  check('再点一次全部展开', secs.every(s => !s.classList.contains('col')));

  // 点标题可单独折叠
  h.dispatchEvent(new win.MouseEvent('click', { bubbles: true }));
  check('点版本标题可单独折叠', secs[0].classList.contains('col') && h.classList.contains('col'));
  h.dispatchEvent(new win.MouseEvent('click', { bubbles: true }));
  check('再点展开', !secs[0].classList.contains('col'));

  // ── 7. 内容完整性：一个字都没少 ────────────────────
  const text = doc.body.textContent;
  const must = ['v4.21.0', 'v4.20.5', 'v4.20.4', 'v4.20.3', 'v4.20.2', 'v4.20.1', 'v4.20.0', 'v4.19.2', 'v4.19.1', 'v4.19.0', 'v4.18.0', 'v4.17.0', 'v4.16.0', 'v4.15.1', 'v4.15.0', 'v4.14.0', 'v4.13.0', 'v4.12.0', 'v4.11.0', 'v4.10.0', 'v4.9.6', 'v4.9.5', 'v4.9', 'v4.8', 'v4.4', 'v3.6', 'v3.5', '视觉精修', 'v35halo', 'v3.4', '实时事件流', '冰敷之后', '210ff68a', 'v3.3', '世界体育报', '622201ee', 'v3.2', '联赛校验', '98693da2', 'focusPlayable', 'v3.1', 'AI 致辞', 'c92a62a5', 'hofVerdict', '版本总览', '附录', '音效技术备忘',
    '14 队加权乐透', '首轮签在交易里送走了', '季池', 'AST 静态审查脚本', 'hoop_life_save_v1'];
  must.forEach(k => check('内容未丢失：' + k, text.indexOf(k) >= 0));
  check('表格数量未变（30 个）', doc.querySelectorAll('table').length === 30,
    String(doc.querySelectorAll('table').length));
  check('卡片数量未变（49 个）', doc.querySelectorAll('.card').length === 49,
    String(doc.querySelectorAll('.card').length));

  // ── 8. 无控制台告警 ───────────────────────────────
  check('无控制台告警', warns.filter(w => !/Not implemented/.test(w)).length === 0, warns.slice(0, 2).join(' | '));

}, { ready: 900, html: require('path').resolve(__dirname, '../更新日志.html') });
