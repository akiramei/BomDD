"""EXP-20261030-02 results section 3 point 3. Usage: python post_check.py <staging-dir>
Count, in each pre/post package pair, the strings that carry each item's criterion (does the post input still carry the defect?)."""
from pathlib import Path

import sys
S = Path(sys.argv[1])  # the staging folder (packages.py output)


def count(pkg, rel_glob, needle):
    n = 0
    for f in (S / pkg).glob(rel_glob):
        if f.is_file():
            n += f.read_text(encoding="utf-8", errors="replace").count(needle)
    return n


checks = [
    # item, (pre, post), glob, needle, what it shows
    ("D1", ("P02", "P04"), "mock/*", "BatchUnassignTag", "unassign action in mock"),
    ("D1", ("P02", "P04"), "mock/*", "N本から外す", "unassign label (static)"),
    ("D1", ("P02", "P04"), "mock/*", "3本から外す", "unassign label"),
    ("D1", ("P02", "P04"), "mock/*", "assignment-state", "assigned/mixed state in chooser"),
    ("D3", ("P10", "P12"), "mock/*", "CreateManualCollection", "create manual collection action"),
    ("D3", ("P10", "P12"), "mock/*", "手動コレクションを作る", "create label"),
    ("D4", ("P14", "P16"), "ruled/10-requirements.yaml", "プレビュー", "preview in requirements"),
    ("D4", ("P14", "P16"), "ruled/10-requirements.yaml", "削除されません", "files-not-deleted notice in requirements"),
    ("D5", ("P18", "P20"), "notes/*", "docked", "'docked' in CAD notes"),
    ("D5", ("P18", "P20"), "ruled/20-spec.md", "docked", "'docked' in spec"),
    ("D6", ("P22", "P24"), "ruled/20-spec.md", "修復で再リンク", "spec hands relink to repair flow"),
    ("D6", ("P22", "P24"), "mock/**/*", "再リンクする", "review mock relinks itself"),
    ("D6", ("P22", "P24"), "mock/**/*", "この候補へ再リンク", "review mock relinks itself (candidate)"),
]
for item, (pre, post), g, needle, what in checks:
    print(f"{item} {what:45s} pre {pre}={count(pre, g, needle):3d}  post {post}={count(post, g, needle):3d}  [{needle}]")
