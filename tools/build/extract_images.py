# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 1
把《篮球人生》单文件里内联的 base64 webp 全部拆成独立文件，HTML 内改为相对路径引用。
- TEAM_CREST  (68 张队徽)      -> assets/crest/NNN.webp
- ACH_ICONS   (18 张成就图标)  -> assets/ach/<key>.webp
- ART_IMG     (19 张场景插图)  -> assets/art/<key>.webp
- heroArt 首屏大图            -> assets/art/hero.webp
"""
import os, re, sys, base64

SRC = os.environ.get('GAME_SRC') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'hoop-life-src', 'game.html')
OUT = os.environ.get('GAME_OUT') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'output')
HTML = os.path.join(OUT, '篮球人生.html')

# 就地覆盖重建（本机 safe-delete 会把 rmtree 拦到回收站，所以不删目录）；
# 收尾会用「磁盘文件集合 == 本轮写出的文件集合」来兜住残留文件。
os.makedirs(OUT, exist_ok=True)

s = open(SRC, encoding='utf-8').read()
orig_len = len(s)

written = {}


def inventory(src):
    """清点「必须原样保留」的符号。拆图只该改图片的值，不该动任何键/别名。
    上一次就是缺了这层检查，ART_IMG.court 别名被静默删掉，线上「球场」图退化成矢量图。"""
    inv = {}
    for name, decl in [('TEAM_CREST', 'const TEAM_CREST={'),
                       ('ACH_ICONS', 'const ACH_ICONS={'),
                       ('ART_IMG', 'const ART_IMG={')]:
        i = src.index(decl)
        e = src.index('};', i) + 2          # base64 字母表里没有 } ; ，不会误命中
        keys = set(re.findall(r'([A-Za-z_$\u4e00-\u9fa5][\w$\u4e00-\u9fa5]*)\s*:', src[i:e]))
        keys.discard('data')                 # data:image/webp 里的 data 是噪声，不是键
        inv[name] = keys
    # 对象后面那批 ART_IMG.xxx= 赋值（含 court 别名）——全文扫，不受长度影响
    inv['ART_IMG.assign'] = set(re.findall(r'ART_IMG\.([A-Za-z_$][\w$]*)\s*=', src))
    for marker in ['ART_IMG.court=ART_IMG.arena;', 'const ACADEMY_CREST=',
                   'function crestData(', 'function crestOf(', 'const ACH_ICON=']:
        inv['存在:' + marker] = {marker: src.count(marker)}
    return inv


BEFORE = inventory(s)


def write_asset(rel, b64):
    path = os.path.join(OUT, rel.replace('/', os.sep))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = base64.b64decode(b64)
    with open(path, 'wb') as f:
        f.write(data)
    written[rel] = len(data)
    return rel


# ---------- 1. TEAM_CREST ----------
i = s.index('const TEAM_CREST={')
j = s.index('const ACADEMY_CREST=', i)
block = s[i:j]
assert block.rstrip().endswith('};'), block[-40:]

pairs = re.findall(r"([^,{}:]+):'(data:image/webp;base64,[A-Za-z0-9+/=]+)'", block)
assert len(pairs) == 68, len(pairs)

crest_entries = []
for n, (key, uri) in enumerate(pairs, 1):
    b64 = uri.split(',', 1)[1]
    rel = write_asset('assets/crest/%03d.webp' % n, b64)
    crest_entries.append("%s:'%s'" % (key.strip(), rel))

new_crest = ('const TEAM_CREST={\n'
             '/* v4.7：队徽改为外链独立 webp（原来是内联 base64，占首屏约 1.4MB）。\n'
             ' * 值里的文件名与下方键名一一对应；序号即原对象里键的出现顺序，替换时未做任何重排。 */\n')
new_crest += ',\n'.join(crest_entries) + '};\n'
s = s[:i] + new_crest + s[j:]

# ---------- 2. ACH_ICONS ----------
i2 = s.index('const ACH_ICONS={')
j2 = s.index('};', i2) + 2
blk2 = s[i2:j2]
pairs2 = re.findall(r"([A-Za-z_$][\w$]*):'(data:image/webp;base64,[A-Za-z0-9+/=]+)'", blk2)
assert len(pairs2) == 18, len(pairs2)
ach_entries = []
for key, uri in pairs2:
    rel = write_asset('assets/ach/%s.webp' % key, uri.split(',', 1)[1])
    ach_entries.append("%s:'%s'" % (key, rel))
new_ach = 'const ACH_ICONS={\n' + ',\n'.join(ach_entries) + '};\n'
s = s[:i2] + new_ach + s[j2:]

# ---------- 3. ART_IMG ----------
# 注意：对象字面量结束的 `};` 和后面那批 ART_IMG.xxx= 之间，还夹着一条别名赋值
#   ART_IMG.court=ART_IMG.arena;   /* 默认球场氛围复用球馆图 */
# 早先版本按「对象开头 → ART_IMG.draft=」整块替换，把这条别名一起删掉了，
# 导致「球场」氛围失去图片、回退成 SVG 矢量图。所以这里只替换对象本身。
i3 = s.index('const ART_IMG={')
e3 = s.index('};', i3) + 2          # 对象字面量自己的结束位置
blk3 = s[i3:e3]
pairs3 = re.findall(r"([A-Za-z_$][\w$]*):'(data:image/webp;base64,[A-Za-z0-9+/=]+)'", blk3)
assert len(pairs3) == 10, len(pairs3)
# 对象后面到 ART_IMG.draft= 之间必须完整保留（原样不动）
_between = s[e3:s.index('ART_IMG.draft=', i3)]
assert 'ART_IMG.court=ART_IMG.arena;' in _between, 'court 别名不见了：%r' % _between
art_entries = []
for key, uri in pairs3:
    rel = write_asset('assets/art/%s.webp' % key, uri.split(',', 1)[1])
    art_entries.append("%s:'%s'" % (key, rel))
new_art = 'const ART_IMG={\n' + ',\n'.join(art_entries) + '};'
s = s[:i3] + new_art + s[e3:]

# ART_IMG.xxx='data:...' 连续行（重新定位：上一步替换后偏移已变）
j3 = s.index('ART_IMG.draft=', i3)
tail = s[j3:]
lines = tail.split('\n')
out_lines = []
n_art2 = 0
for ln in lines:
    m = re.match(r"ART_IMG\.([A-Za-z_$][\w$]*)='(data:image/webp;base64,[A-Za-z0-9+/=]+)';", ln)
    if m:
        key, uri = m.group(1), m.group(2)
        rel = write_asset('assets/art/%s.webp' % key, uri.split(',', 1)[1])
        out_lines.append("ART_IMG.%s='%s';" % (key, rel))
        n_art2 += 1
    else:
        out_lines.append(ln)
assert n_art2 == 9, n_art2
s = s[:j3] + '\n'.join(out_lines)

# ---------- 4. 首屏 heroArt 大图 ----------
m = re.search(r'<img src="(data:image/webp;base64,[A-Za-z0-9+/=]+)" alt="">', s)
assert m
rel = write_asset('assets/art/hero.webp', m.group(1).split(',', 1)[1])
s = s[:m.start()] + '<img src="%s" alt="" decoding="async">' % rel + s[m.end():]

# ---------- 5. 懒加载属性 ----------
reps = [
    ("""'<img class="tcrest" src="'+c+'" alt="">'""",
     """'<img class="tcrest" src="'+c+'" alt="" loading="lazy" decoding="async">'"""),
    ("""'<img src="'+crestData(t)+'" alt="">'""",
     """'<img src="'+crestData(t)+'" alt="" loading="lazy" decoding="async">'"""),
    ("""<img src="${_ic}" alt="">""",
     """<img src="${_ic}" alt="" loading="lazy" decoding="async">"""),
    ("""'<img class="artimg" src="'+photo+'" alt="">'""",
     """'<img class="artimg" src="'+photo+'" alt="" decoding="async">'"""),
]
for a, b in reps:
    cnt = s.count(a)
    assert cnt == 1, (a, cnt)
    s = s.replace(a, b)

# ---------- 6. 校验：不应再有 data:image ----------
left = len(re.findall(r'data:image/', s))
if left:
    raise SystemExit('仍有 %d 处内联图片未拆出' % left)

# ---------- 7. 硬闸：所有符号必须一个不少 ----------
AFTER = inventory(s)
bad = []
for k in BEFORE:
    if BEFORE[k] != AFTER[k]:
        bad.append('%s: %r -> %r' % (k, BEFORE[k], AFTER[k]))
if bad:
    raise SystemExit('改动丢失了原有符号，已中止：\n  ' + '\n  '.join(bad))

# 图片数量：直接用「源文件里内联图片的总数」当基准（106），不靠推算
ORIG_IMAGES = len(re.findall(r'data:image/webp;base64,', open(SRC, encoding='utf-8').read()))
if len(written) != ORIG_IMAGES:
    raise SystemExit('图片数量对不上：写出 %d，源文件内联 %d' % (len(written), ORIG_IMAGES))

os.makedirs(OUT, exist_ok=True)
with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(s)

# ---------- 8. 磁盘上不允许有本轮之外的多余图片 ----------
on_disk = set()
for root, _, fs in os.walk(os.path.join(OUT, 'assets')):
    for f in fs:
        on_disk.add(os.path.relpath(os.path.join(root, f), OUT).replace('\\', '/'))
extra = sorted(on_disk - set(written))
if extra:
    raise SystemExit('输出目录里有本轮没写出的残留文件（%d 个）：%s' % (len(extra), extra[:5]))

print('符号保全检查: 通过（%d 项）' % len(BEFORE))
print('图片文件: %d 张, 合计 %.0f KB' % (len(written), sum(written.values()) / 1024))
print('HTML: %.0f KB -> %.0f KB' % (orig_len / 1024, len(s) / 1024))
