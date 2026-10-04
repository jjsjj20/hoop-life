# -*- coding: utf-8 -*-
"""
R4 交付欠账：腾讯文档同步脚本（更新日志.md / 开发计划.md → docs.qq.com）。

前置：WorkBuddy 的「腾讯文档」连接器已启用授权（否则 tdoc_init 报
provider personal=connector_disabled——请先在 WorkBuddy 连接器管理里启用）。

用法（在仓库根）：
  python tools/sync_tdocs.py                # 同步 更新日志.md + 开发计划.md
  python tools/sync_tdocs.py 文件1.md ...   # 同步指定文件

流程（来自 tencent-docs-md-sync skill 的实战经验）：
  ① 覆盖 TDOC_API_BASE_URL=https://docs.qq.com（宿主下发域名可能 502）；
  ② 本地文件走「导入」通道（import_file → manage.async_import → 轮询进度），
    不用 create_*（会带模板垃圾）；
  ③ 产出 https://docs.qq.com/markdown/<id> 链接。
"""
import io
import json
import os
import subprocess
import sys
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DEFAULT_FILES = ['更新日志.md', '开发计划.md']

SKILL_CANDIDATES = [
    r'C:\Users\Mayn\.workbuddy\plugins\cache\workbuddy-builtin\tencent-docs-plugin',
]


def find_skill_dir():
    for base in SKILL_CANDIDATES:
        for r, ds, _ in os.walk(base):
            if 'tencentdocs.py' in ds or 'tencentdocs.py' in (os.listdir(r) if os.path.isdir(r) else []):
                if os.path.exists(os.path.join(r, 'tencentdocs.py')):
                    return r
    return None


def run(py, cwd, args):
    env = dict(os.environ)
    env.setdefault('TDOC_API_BASE_URL', 'https://docs.qq.com')
    r = subprocess.run([py, cwd and os.path.join(cwd, args[0]) or args[0]] + args[1:],
                       capture_output=True, text=True, encoding='utf-8', errors='replace',
                       cwd=cwd, env=env)
    return r


def main():
    files = sys.argv[1:] or DEFAULT_FILES
    skill = find_skill_dir()
    if not skill:
        raise SystemExit('!! 找不到 tencent-docs skill 脚本目录（tencentdocs.py）')
    py = sys.executable

    for f in files:
        fp = os.path.join(REPO, f) if not os.path.isabs(f) else f
        if not os.path.exists(fp):
            print('!! 跳过不存在的', f)
            continue
        print('══ 同步', os.path.basename(fp), '══')
        r = run(py, skill, ['import_file.py', fp])
        out = (r.stdout or '') + (r.stderr or '')
        print(out.strip()[-500:])
        fields = dict(re.findall(r'^(?:🔑 |📦 )?(\w+):\s*(.+)$', out, re.M) and
                      [(m.group(1), m.group(2)) for m in
                       __import__('re').finditer(r'^(\w+): (.+)$', out, re.M)])
        need = ['task_id', 'file_key', 'file_name', 'file_md5', 'file_size']
        if not all(k in fields for k in ['task_id', 'file_key']):
            # import_file.py 的输出键为 TASK_ID/FILE_KEY/FILE_NAME/FILE_MD5/FILE_SIZE
            fields = dict(re.findall(r'^(TASK_ID|FILE_KEY|FILE_NAME|FILE_MD5|FILE_SIZE|IMPORT_READY):\s*(.+)$',
                                     out, re.M))
            fields = {k.lower(): v for k, v in fields.items()}
        if 'task_id' not in fields:
            print('!! 未取得导入凭据，跳过该文件')
            continue
        payload = json.dumps({
            'task_id': fields['task_id'], 'file_key': fields['file_key'],
            'file_name': fields.get('file_name', os.path.basename(fp)),
            'file_md5': fields.get('file_md5', ''), 'file_size': int(fields.get('file_size', 0)),
        })
        r2 = run(py, skill, ['tencentdocs.py', 'tdoc_call', 'tencent-docs',
                             'manage.async_import', payload])
        print((r2.stdout or '').strip()[-300:])
        url = None
        for _ in range(20):
            time.sleep(2)
            r3 = run(py, skill, ['tencentdocs.py', 'tdoc_call', 'tencent-docs',
                                 'manage.import_progress',
                                 json.dumps({'task_id': fields['task_id'], 'file_key': fields['file_key']})])
            txt = (r3.stdout or '')
            if '"progress": 100' in txt or '"progress":100' in txt:
                import re as _re
                m = _re.search(r'https://docs\.qq\.com/markdown/[\w-]+', txt)
                url = m.group(0) if m else '（已完成）'
                break
        print('✅', os.path.basename(fp), '→', url or '（轮询超时，请到 docs.qq.com 查看最近导入）')
    print('\n完成。')


if __name__ == '__main__':
    main()
