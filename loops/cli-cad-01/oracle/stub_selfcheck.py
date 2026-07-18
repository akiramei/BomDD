#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""stub_selfcheck.py — oracle.py の機構自己検証専用のダミー CLI(監査用に残置)。

目的: subprocess 呼び出し・セクション分割・PASS/FAIL 集計・exit code 伝播が
動くことの確認のみ。**期待値の導出根拠には一切使っていない**(期待値は
kit/cli-cad.md の解析規則を fixtures へ手で適用して導出 — oracle-notes.md 参照)。
入力ファイルは読まず、常に固定の全ゼロ出力を返す。仕様適合実装ではない。
"""
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

args = sys.argv[1:]

if args and args[0] == "--selftest":
    print("selftest: PASS")
    sys.exit(0)

if args and args[0] == "show":
    if len(args) < 2:
        print("usage: worklist.py show <ID> [PATH]")
        sys.exit(0)
    print("not found: {}".format(args[1]))
    sys.exit(0)

print("== worklist(open / watch)==")
print("(0 件)")
print("== actions due(要処理 — 記帳は正常)==")
print("(0 件)")
print("== validation warnings(記帳不整合)==")
print("(0 件)")
print("== legacy coverage ==")
print("(legacy 節なし)")
print("== stats ==")
print("sections_scanned: 0")
print("structured_sections: 0")
print("audited_legacy_sections: 0")
print("unaudited_legacy_sections: 0")
print("open_items: 0(native 0 / migrated 0)")
print("watch_items: 0(native 0 / migrated 0)")
print("actions_due: 0")
print("closed_items: 0(recovered/withdrawn/superseded)")
print("validation_warnings: 0")
print("elapsed_ms: 0")
sys.exit(0)
