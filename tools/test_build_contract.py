#!/usr/bin/env python3
"""Small regression checks for the release and cache contracts."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build_all  # noqa: E402


def check(label, condition):
    if not condition:
        raise AssertionError(label)
    print("[ok] " + label)


check("current changelog version parses", build_all.release_version("当前版本 **v5.0.6**") == "v5.0.6")
check("legacy colon version parses", build_all.release_version("当前版本： **v4.17.0**") == "v4.17.0")
check("unmarked version is rejected", build_all.release_version("当前版本 v5.0.6") is None)

patch = (ROOT / "tools" / "build" / "patch_pwa.py").read_text(encoding="utf-8")
check("service worker cleanup is scoped", "k.indexOf('hoop-life-') === 0 && k !== CACHE" in patch)
print("build contracts passed")
