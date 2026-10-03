# -*- coding: utf-8 -*-
"""
hoop-life 改造 step 3：按「实际显示尺寸」重采样资源图片。

源图是照更大的展示场景准备的，而 CSS 里它们实际只用这么点：
    .tcrest   20×20（h3 里 23×23）   源 144×144 → 超标 7.2 倍
    .achic    34×34                  源 128×128 → 超标 3.8 倍
    .artimg   最宽约 634 × 128 高     源 1600×400 → 超标 2.5 倍
    .heroArt  约 960×270             源 1600×578 → 1.7 倍，够用，不动

统一按 2 倍屏留余量重采样，清晰度基本无损，但字节数大幅下降——
尤其是队徽：一场「球队图鉴」会同时拉 68 张，这是"图片加载缓慢"的主要来源。
"""
import os, io, sys
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(os.environ.get('GAME_OUT') or os.path.join(BASE, '..', 'output'), 'assets')

# (子目录, 目标宽, 目标高, 说明)
PLAN = [
    ('crest', 48, 48, '队徽 · 实际显示 20-23px'),
    ('ach',   72, 72, '成就图标 · 实际显示 34px'),
    ('art', 1280, 320, '场景插画 · 实际显示约 634×128'),
]
# 这几张不使用 (art 目录的横图)，单独跳过
SKIP = {'art/hero.webp'}

QUALITY = 88


def webp_size(path):
    with open(path, 'rb') as f:
        d = f.read(40)
    c = d[12:16]
    if c == b'VP8X':
        return int.from_bytes(d[24:27], 'little') + 1, int.from_bytes(d[27:30], 'little') + 1
    if c == b'VP8 ':
        import struct
        return struct.unpack('<H', d[26:28])[0] & 0x3fff, struct.unpack('<H', d[28:30])[0] & 0x3fff
    if c == b'VP8L':
        b = int.from_bytes(d[21:25], 'little')
        return (b & 0x3fff) + 1, ((b >> 14) & 0x3fff) + 1
    return None


before_total = after_total = 0
rows = []
for sub, tw, th, note in PLAN:
    d = os.path.join(ASSETS, sub)
    if not os.path.isdir(d):
        raise SystemExit('找不到目录：' + d)
    for fn in sorted(os.listdir(d)):
        if not fn.lower().endswith('.webp'):
            continue
        rel = '%s/%s' % (sub, fn)
        if rel in SKIP:
            continue
        p = os.path.join(d, fn)
        b0 = os.path.getsize(p)
        src = webp_size(p)
        im = Image.open(p)
        im.load()
        # 高度按比例缩放，宽度不超过目标宽（两条边都不放大）
        scale = min(tw / im.width, th / im.height, 1.0)
        if scale >= 1.0:
            # 已经不比目标大 → 原样跳过。这条保证脚本可重复执行：
            # 每重编码一次都会掉一点画质，绝不能跑两遍就压两遍。
            before_total += b0
            after_total += b0
            rows.append((rel, src, (im.width, im.height), b0, b0))
            continue
        nw, nh = max(1, round(im.width * scale)), max(1, round(im.height * scale))
        if im.mode not in ('RGB', 'RGBA'):
            im = im.convert('RGBA' if 'A' in im.getbands() else 'RGB')
        if scale < 1.0:
            im = im.resize((nw, nh), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, 'WEBP', quality=QUALITY, method=6)
        data = buf.getvalue()
        # 只有确实变小才落盘，避免个别图反而变大
        if len(data) < b0:
            with open(p, 'wb') as f:
                f.write(data)
        b1 = os.path.getsize(p)
        before_total += b0
        after_total += b1
        rows.append((rel, src, (im.width, im.height), b0, b1))

# hero 只统计，不改
h = os.path.join(ASSETS, 'art', 'hero.webp')
if os.path.exists(h):
    before_total += os.path.getsize(h)
    after_total += os.path.getsize(h)

print('%-26s %-12s %-12s %10s %10s' % ('文件', '源尺寸', '新尺寸', '原', '新'))
for rel, src, dst, b0, b1 in rows:
    flag = '' if b1 < b0 else '  (未缩小，保持原样)'
    print('%-26s %-12s %-12s %8.1fK %8.1fK%s' % (
        rel, '%dx%d' % src if src else '?', '%dx%d' % dst, b0 / 1024, b1 / 1024, flag))

print()
print('重采样 %d 张：%.0f KB → %.0f KB（省 %.0f%%，约 %.0f KB）' % (
    len(rows), before_total / 1024, after_total / 1024,
    (1 - after_total / before_total) * 100, (before_total - after_total) / 1024))
