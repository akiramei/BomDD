#!/usr/bin/env python3
"""kit-freshness — 同梱 kit の完全性・鮮度検査(harness ECO-026)

製品リポで実行し、bomdd.lock と kit-manifest.json を入力に 4 値判定を返す
(playbook §13「4 値判定+理由コード」— UNKNOWN を FRESH へ丸めない):

  FRESH    — kit は manifest と一致・origin HEAD と lock commit が一致
  STALE    — kit は manifest と一致・origin が先行(behind N)。凍結は設計(ECO-004)で
             あり STALE 自体は不適合ではない(advisory)— 更新の要否は設置先の裁定・
             更新手順は手動 3 手順(正本複写 → kit/lock 再生成 → 再適格)
  TAMPERED — kit 実体が manifest と乖離(改変・欠落・余剰 — fail-closed 双方向)
  UNKNOWN  — origin 不達・commit 不明等で鮮度が測定不能(理由コード付き)

exit 契約(意味写像の明示 — silence §10 CLI 終了契約):
  0 = 判定成功(FRESH / STALE)
  1 = TAMPERED
  2 = 入力不正(bomdd.lock / kit-manifest.json 不在・パース不能・構造不正)
  3 = UNKNOWN(理由コード: ORIGIN_MISSING / ORIGIN_NOT_GIT / COMMIT_UNKNOWN /
      GIT_UNAVAILABLE / DIVERGED)

既知限界(宣言+掃射手段の紐づけ — control-plan「検査器の既知限界」):
  - origin_path は来歴であり実行時依存ではない(bomdd.lock 冒頭の宣言)。origin が
    ローカルに存在しない環境(CI・別マシン)では鮮度は原理的に UNKNOWN — これは
    fail-open ではなく「測定不能の明示」。完全性(TAMPERED 検出)は origin なしで機能する。
  - nested Git 環境(hook 内実行等)対策: origin への git 呼び出しは
    `git rev-parse --local-env-vars` の全変数を除去した環境で行う
    (ViewTube ECO-VT-027 の教訓 — 手維持の部分集合にしない。OBS-20260727-02 系譜)。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import yaml

# 検査は自分の前提を自分で満たす(OBS-20260727-10): Windows の子プロセス stdout は
# ロケール既定(cp932 等)になり、日本語・記号の print が UnicodeEncodeError で
# 検査自体を落とす — 出力エンコーディングを自前で固定する。
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def _clean_git_env() -> dict | None:
    """repo-local な Git 環境変数を全除去した環境を返す(git 不能なら None)。"""
    try:
        p = subprocess.run(["git", "rev-parse", "--local-env-vars"],
                           capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if p.returncode != 0:
        return None
    env = dict(os.environ)
    for name in p.stdout.split():
        env.pop(name, None)
    return env


def _git(origin: Path, args: list[str], env: dict) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(origin)] + args,
                          capture_output=True, text=True, timeout=60, env=env)


def main() -> int:
    ap = argparse.ArgumentParser(description="同梱 kit の完全性・鮮度検査(4 値判定)")
    ap.add_argument("--root", default=".", help="製品リポのルート(bomdd.lock の所在)")
    a = ap.parse_args()
    root = Path(a.root).resolve()

    # --- 入力(exit 2 = 入力不正) -----------------------------------------------------
    lock_path = root / "bomdd.lock"
    if not lock_path.is_file():
        print(f"kit-freshness: INPUT_ERROR reason=LOCK_MISSING path={lock_path}")
        return 2
    try:
        lock = yaml.safe_load(lock_path.read_text(encoding="utf-8"))["bomdd_lock"]
        kit_root = root / lock["kit"]["root"]
        manifest_path = root / lock["kit"]["manifest"]
        lock_commit = str(lock["method"]["commit"])
        origin = Path(str(lock["method"]["origin_path"]))
    except (yaml.YAMLError, KeyError, TypeError) as e:
        print(f"kit-freshness: INPUT_ERROR reason=LOCK_INVALID detail={str(e)[:120]}")
        return 2
    if not manifest_path.is_file():
        print(f"kit-freshness: INPUT_ERROR reason=MANIFEST_MISSING path={manifest_path}")
        return 2
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))["files"]
    except (json.JSONDecodeError, KeyError) as e:
        print(f"kit-freshness: INPUT_ERROR reason=MANIFEST_INVALID detail={str(e)[:120]}")
        return 2

    # --- 完全性(exit 1 = TAMPERED・fail-closed 双方向) -------------------------------
    problems: list[str] = []
    for rel, expected in manifest.items():
        f = kit_root / rel
        if not f.is_file():
            problems.append(f"missing:{rel}")
        elif hashlib.sha256(f.read_bytes()).hexdigest() != expected:
            problems.append(f"modified:{rel}")
    listed = set(manifest)
    for f in kit_root.rglob("*"):
        if f.is_file():
            rel = f.relative_to(kit_root).as_posix()
            if rel not in listed and f != manifest_path:
                problems.append(f"extra:{rel}")
    lock_manifest_sha = str(lock["kit"].get("manifest_sha256", ""))
    if hashlib.sha256(manifest_path.read_bytes()).hexdigest() != lock_manifest_sha:
        problems.append("modified:kit-manifest.json(lock の manifest_sha256 と不一致)")
    if problems:
        print(f"kit-freshness: TAMPERED reason=MANIFEST_MISMATCH count={len(problems)} "
              f"first={problems[:5]}")
        return 1

    # --- 鮮度(exit 0 = FRESH/STALE・exit 3 = UNKNOWN) --------------------------------
    env = _clean_git_env()
    if env is None:
        print("kit-freshness: UNKNOWN reason=GIT_UNAVAILABLE(完全性は PASS — 鮮度のみ測定不能)")
        return 3
    if not origin.is_dir():
        print(f"kit-freshness: UNKNOWN reason=ORIGIN_MISSING origin={origin}"
              "(完全性は PASS — 鮮度のみ測定不能)")
        return 3
    if _git(origin, ["rev-parse", "--is-inside-work-tree"], env).returncode != 0:
        print(f"kit-freshness: UNKNOWN reason=ORIGIN_NOT_GIT origin={origin}")
        return 3
    if _git(origin, ["rev-parse", "--verify", f"{lock_commit}^{{commit}}"], env).returncode != 0:
        print(f"kit-freshness: UNKNOWN reason=COMMIT_UNKNOWN commit={lock_commit[:12]}")
        return 3
    head = _git(origin, ["rev-parse", "HEAD"], env).stdout.strip()
    if head == lock_commit:
        print(f"kit-freshness: FRESH commit={lock_commit[:12]}(origin HEAD と一致)")
        return 0
    behind = _git(origin, ["rev-list", "--count", f"{lock_commit}..HEAD"], env)
    n = behind.stdout.strip() if behind.returncode == 0 else None
    if n is None or n == "0":
        print(f"kit-freshness: UNKNOWN reason=DIVERGED lock={lock_commit[:12]} head={head[:12]}"
              "(HEAD 不一致かつ先行 0 — origin の履歴書き換えの疑い)")
        return 3
    print(f"kit-freshness: STALE behind={n} lock={lock_commit[:12]} head={head[:12]}"
          "(advisory — 更新の要否は設置先の裁定・手順は手動 3 手順)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
