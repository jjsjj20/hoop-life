# -*- coding: utf-8 -*-
"""R4：从 git 历史补打 v4.9.6~v4.16.0 各版本的 ZIP 交付包。
每个版本取「更新日志.当前版本 == 该版本」的最后一个提交，用 git archive 打包
（游戏 + 资源 + manifest/sw/icons + 两份日志 + 构建说明），输出到工作区根目录。"""
import io
import os
import re
import subprocess
import zipfile

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUTDIR = os.path.abspath(os.path.join(REPO, '..'))   # 工作区根（与 hoop-life-v4.9.5.zip 同级）
TARGETS = ['v4.9.6', 'v4.10.0', 'v4.11.0', 'v4.12.0', 'v4.13.0', 'v4.14.0', 'v4.15.0', 'v4.15.1', 'v4.16.0']


def git(args):
    r = subprocess.run(['git', '-C', REPO] + args, capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    if r.returncode != 0:
        raise SystemExit('git ' + ' '.join(args) + ' 失败：' + (r.stderr or '')[:300])
    return r.stdout


def ver_at(commit):
    """该提交时 更新日志.md 头部声明的当前版本。"""
    r = subprocess.run(['git', '-C', REPO, 'show', commit + ':更新日志.md'],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode != 0:
        return None
    m = re.search(r'当前版本：\*\*(v[\d.]+)\*\*', r.stdout)
    return m.group(1) if m else None


def paths_at(commit):
    out = git(['-c', 'core.quotepath=off', 'ls-tree', '-r', '--name-only', commit])
    paths = set()
    for ln in out.split('\n'):
        ln = ln.strip()
        if not ln:
            continue
        if ln == '篮球人生.html' or ln.startswith('assets/') or ln in (
                '更新日志.md', '更新日志.html', 'README-build.md', 'manifest.json', 'sw.js'):
            paths.add(ln)
        elif ln.startswith('icons/'):
            paths.add(ln)
    return paths


# 1) 版本 → 该版本的最后一个提交
commits = [c for c in git(['log', '--format=%H', '-n', '200']).split('\n') if c.strip()]
ver2commit = {}
for c in commits:
    v = ver_at(c)
    if v:                                # 倒序遍历：越遇越早——保留「日志首次声明 vX」的提交（=该版本最终代码+日志）
        ver2commit[v] = c

# 2) 逐版本打 ZIP
made = []
for v in TARGETS:
    out_zip = os.path.join(OUTDIR, 'hoop-life-%s.zip' % v)
    if os.path.exists(out_zip):
        print('已存在，跳过：', os.path.basename(out_zip))
        continue
    c = ver2commit.get(v)
    if not c:
        print('!! 找不到 %s 对应的提交，跳过' % v)
        continue
    paths = sorted(paths_at(c))
    if not paths:
        print('!! %s 在 %s 无可打包文件' % (v, c[:8]))
        continue
    if os.path.exists(out_zip):
        os.remove(out_zip)
    r = subprocess.run(['git', '-C', REPO, 'archive', '--format=zip', '-o', out_zip, c] + paths,
                       capture_output=True, text=True)
    if r.returncode != 0:
        print('!! archive 失败 %s：' % v, (r.stderr or '')[:200])
        continue
    z = zipfile.ZipFile(out_zip)
    n = len(z.namelist())
    made.append((v, c[:8], n))
    print('hoop-life-%s.zip  ←  %s（%d 项）' % (v, c[:8], n))

print('\n补打完成：%d 个 ZIP' % len(made))
