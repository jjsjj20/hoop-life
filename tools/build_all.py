#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一条命令重建《篮球人生 · 生涯模拟》。

    python3 tools/build_all.py

  产物在 dist/：篮球人生.html + assets/（106 张 webp）
  可选参数：
    --src  原版游戏文件（默认 src/篮球人生-v4.8-原版.html）
    --out  输出目录（默认 dist/）
    --skip-optimize  跳过图片重采样（需要 Pillow；没装就自动跳过并警告）

重建后的产物应与仓库根的 篮球人生.html 逐字节一致——脚本最后会自动比对并打印结果。
"""
import argparse
import hashlib
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "tools", "build")

STEPS = [
    ("extract_images.py",       "① 拆出内联图片",            True),
    ("patch_keyboard_save.py",  "② 键盘操作 + 存档导入导出",   True),
    ("patch_perf.py",           "③ 首屏图片加载时序",          True),
    ("patch_robustness.py",     "④ 异常可见性 + AI 密钥提示",  True),
    ("patch_draft_lottery.py",  "⑤ 真实签位系统",            True),
    ("patch_pick_events.py",    "⑥ 签位主题事件",            True),
    ("patch_audit_fixes.py",    "⑦ 选秀数据工厂收敛（自查修复）", True),
    ("patch_drama_quota.py",    "⑧ 戏剧配额防饿死（M1 调参）",  True),
    ("patch_remove_coach.py",   "⑨ 彻底移除教练模式",         True),
    ("patch_pick_trades.py",    "⑩ 签位资产板 + 签位交易",     True),
    ("patch_share_card.py",     "⑪ 生涯分享卡",              True),
    ("patch_p4_polish.py",      "⑫ P4 收尾（缩放+工厂收敛）",   True),
    ("patch_content_p5.py",     "⑬ P5 内容补给 + 次轮归属播报", True),
    ("patch_p7.py",             "⑭ P7 签位延伸 + 排名缓存分槽", True),
    ("patch_card_png.py",       "⑮ 分享卡图片版（Canvas PNG）", True),
    ("patch_pwa.py",            "⑯ PWA 离线（manifest+SW+图标）", True),
    ("patch_r3.py",             "⑰ R3 摆烂机制实装",           True),
    ("patch_qingxun.py",        "⑱ R2 青训体验补强",           True),
    ("patch_ui_tidy.py",        "⑲ UI 减负（行动栏 15→5 + ☰ 更多）", True),
    ("patch_ui_mobile.py",      "⑳ 移动端布局（HUD 收起/行动栏吸底）", True),
    ("patch_continue.py",       "㉑ 移动端「继续」吸底",        True),
    ("patch_result_fold.py",    "㉒ 移动端结果页剧情折叠",      True),
    ("patch_difficulty.py",     "㉓ 难度重做（成长/NPC/续战）",  True),
    ("patch_honors.py",         "㉔ 荣誉与冠军校准",            True),
    ("patch_sw_cache.py",       "㉕ SW 缓存名=最终产物哈希",    True),
    ("optimize_images.py",      "㉖ 图片按显示尺寸重采样",      False),   # 需要 Pillow，单独处理
]


def sha16(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def main():
    ap = argparse.ArgumentParser(description="重建《篮球人生》")
    ap.add_argument("--src", default=os.path.join(ROOT, "src", "篮球人生-v4.8-原版.html"))
    ap.add_argument("--out", default=os.path.join(ROOT, "dist"))
    ap.add_argument("--skip-optimize", action="store_true")
    ap.add_argument("--zip", action="store_true",
                    help="同时打包 ZIP 交付包（游戏+资源+manifest/sw/icons+两份日志+构建说明）")
    args = ap.parse_args()

    if not os.path.exists(args.src):
        print("找不到原版源文件：%s\n（可用 --src 指定）" % args.src)
        return 1

    env = dict(os.environ, GAME_SRC=args.src, GAME_OUT=args.out,
               GAME_HTML=os.path.join(args.out, "篮球人生.html"), PYTHONIOENCODING="utf-8")

    print("══ 重建《篮球人生》══════════════════════════════")
    print("  源:  %s" % os.path.relpath(args.src, ROOT))
    print("  出:  %s" % os.path.relpath(args.out, ROOT))
    print()

    have_pillow = True
    try:
        import PIL  # noqa: F401
    except ImportError:
        have_pillow = False

    for script, title, required in STEPS:
        if script == "optimize_images.py" and not have_pillow:
            print("⊘ %s —— 未安装 Pillow，跳过（pip install Pillow 后可重跑）" % title)
            continue
        if script == "optimize_images.py" and args.skip_optimize:
            print("⊘ %s —— 按 --skip-optimize 跳过" % title)
            continue
        print("▶ %s" % title)
        r = subprocess.run([sys.executable, os.path.join(BUILD, script)],
                           env=env, capture_output=True, text=True, encoding="utf-8")
        out = (r.stdout or "").strip()
        if out:
            print("\n".join("   " + line for line in out.split("\n")))
        if r.returncode != 0:
            print("\n✗ 该步骤失败（退出码 %d）\n%s" % (r.returncode, (r.stderr or "")[-1500:]))
            return 1
        print()

    # ── 校验产物 ────────────────────────────────────────
    product = os.path.join(args.out, "篮球人生.html")
    if not os.path.exists(product):
        print("✗ 没有生成 %s" % product)
        return 1

    print("══ 产物校验 ═════════════════════════════════════")
    print("  篮球人生.html  %.1f KB" % (os.path.getsize(product) / 1024))
    assets = 0
    for root, _, files in os.walk(os.path.join(args.out, "assets")):
        assets += len(files)
    print("  assets 资源    %d 张" % assets)

    ref = os.path.join(ROOT, "篮球人生.html")
    if os.path.exists(ref):
        same = sha16(product) == sha16(ref)
        print("  与仓库根的成品一致: %s" % ("✓ 是" if same else "✗ 否（可能是版本不同步）"))
        if not same:
            return 1

    # ── R1（v4.15.1）：--zip 自动打包交付包（版本号取自更新日志） ──
    if args.zip:
        import re as _re
        import zipfile as _zipfile
        ver = None
        md_path = os.path.join(ROOT, "更新日志.md")
        if os.path.exists(md_path):
            with open(md_path, encoding="utf-8") as f:
                m = _re.search(r"当前版本：\*\*(v[\d.]+)\*\*", f.read())
            if m:
                ver = m.group(1)
        zip_path = os.path.join(args.out, "hoop-life-%s.zip" % (ver or "dev"))
        if os.path.exists(zip_path):
            os.remove(zip_path)
        with _zipfile.ZipFile(zip_path, "w", _zipfile.ZIP_DEFLATED) as z:
            z.write(product, "篮球人生.html")
            for extra in ("manifest.json", "sw.js"):
                p2 = os.path.join(args.out, extra)
                if os.path.exists(p2):
                    z.write(p2, extra)
            for sub in ("icons", "assets"):
                d2 = os.path.join(args.out, sub)
                if os.path.isdir(d2):
                    for r2, _, fs2 in os.walk(d2):
                        for f2 in fs2:
                            full = os.path.join(r2, f2)
                            z.write(full, os.path.relpath(full, args.out))
            for md in ("更新日志.md", "更新日志.html", "README-build.md"):
                p2 = os.path.join(ROOT, md)
                if os.path.exists(p2):
                    z.write(p2, md)
        print("  ZIP 交付包: %s（%d 项）" % (os.path.basename(zip_path), len(_zipfile.ZipFile(zip_path).namelist())))

    print("\n✅ 重建完成。产物在 %s/" % os.path.relpath(args.out, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
