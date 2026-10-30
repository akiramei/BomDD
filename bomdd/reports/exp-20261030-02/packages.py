"""EXP-20261030-02 - build the inspector packages (definitions.md sections 2-4).

Usage: python packages.py <staging-dir>
Reads every input with `git show <commit>:<path>` (never a working tree), writes one folder per (item, state, arm) under
<staging-dir>, and writes manifest.json next to this file (each staged file with its source and SHA-256). Refuses (exit 2) a
required file that does not exist at its commit.
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPOS = HERE.parents[3]
BOMDD = HERE.parents[2]
PROMPT_SRC = BOMDD / "method" / "prompts" / "ui-mock-coverage.md"

VT_NOTES = ["bomdd/ui/design-intent.md", "bomdd/ui/unresolved-questions.md", "?bomdd/ui/videos-cad.md"]
VT_MOCK = ["bomdd/ui/mock/viewtube-v1.html"]
RULED = ["bomdd/10-requirements.yaml", "bomdd/20-spec.md"]

# item: (product, {state: (product commit, ui repo commit or None)}, notes, mocks); "?" = where it exists, "dir/" = every file under it
ITEMS = {
    "D1": ("ViewTube", {"pre": ("ad8c37c", None), "post": ("6f24075f", None)}, VT_NOTES, VT_MOCK),
    "D2": ("ViewTube", {"pre": ("2060849", None), "post": ("b9f629d6", None)}, VT_NOTES, VT_MOCK),
    "D3": ("ViewTube", {"pre": ("05e2d905", None), "post": ("1cd3e7a5", None)}, VT_NOTES, VT_MOCK),
    "D4": ("ViewPrism2", {"pre": ("19c436f", "7ffd423"), "post": ("bd573d6", "7ffd423")},
           ["docs/screens/image_tab.md", "docs/screens/work_tab.md"],
           ["資料/画像タブ/ViewPrism2 画像タブ.dc.html", "資料/画像タブ/ViewPrism2 整理マージ (standalone).html",
            "資料/作業タブ/ViewPrism2 作業タブ.html"]),
    "D5": ("ViewPrism2", {"pre": ("872d33c", "2c31176"), "post": ("403756a", "c9b5667")},
           ["docs/screens/image_tab.md", "docs/screens/work_tab.md"],
           ["資料/画像タブ/ViewPrism2 画像タブ.dc.html"]),
    "D6": ("ViewPrism2", {"pre": ("6866b2f", "5556df2"), "post": ("58354ed", "3a1bb37")},
           ["docs/screens/pending_review.md", "?docs/screens/integrity_review.md"],
           ["資料/未裁定の画像/", "?資料/要確認の画像/"]),
}

ARM_B_RESTRICTION = ("本検査では、要求(ruled/10-requirements.yaml)と仕様(ruled/20-spec.md)もモックパッケージの一部である。"
                     "検査対象は「モックが語っていること」と「要求・仕様が語っていること」である。")
ARM_B_LAYER1 = ("- 要求・仕様とモック(注記・DOM)の間の矛盾と、要求・仕様が求めるのにモックに無いもの、"
                "モックにあるのに要求・仕様が述べないものも列挙する")


def git(repo, *args):
    return subprocess.run(["git", "-C", str(REPOS / repo), *args], capture_output=True, check=True).stdout


def exists(repo, commit, path):
    return subprocess.run(["git", "-C", str(REPOS / repo), "cat-file", "-e", f"{commit}:{path}"],
                          capture_output=True).returncode == 0


def list_dir(repo, commit, prefix):
    out = git(repo, "-c", "core.quotepath=false", "ls-tree", "-r", "--name-only", commit, "--", prefix).decode("utf-8")
    return [p for p in out.splitlines() if p]


def expand(repo, commit, specs):
    files = []
    for spec in specs:
        optional = spec.startswith("?")
        path = spec.lstrip("?")
        found = list_dir(repo, commit, path) if path.endswith("/") else ([path] if exists(repo, commit, path) else [])
        if not found and not optional:
            sys.stderr.write(f"UNMEASURABLE: {repo}@{commit}:{path} missing\n")
            sys.exit(2)
        files += found
    return files


def reduce_standalone(raw):
    """A standalone bundle -> its authored page (the decoded __bundler/template); other content unchanged."""
    text = raw.decode("utf-8")
    m = re.search(r'<script type="__bundler/template">(.*?)</script>', text, re.S)
    if not m:
        return raw, None
    return json.loads(m.group(1)).encode("utf-8"), "standalone bundle reduced to its __bundler/template (runtime and fonts dropped)"


def prompt(arm, has_ruled):
    src = PROMPT_SRC.read_text(encoding="utf-8")
    body = src[src.index("あなたは UI モックの受入検査官である"):]
    if arm == "B":
        anchor = "検査対象は「モックが語っていること」だけである。"
        layer1 = "- 状態モデリングの部品間非対称"
        if anchor not in body or layer1 not in body:
            sys.stderr.write("UNMEASURABLE: the prompt's anchors changed\n")
            sys.exit(2)
        body = body.replace(anchor, ARM_B_RESTRICTION, 1)
        i = body.index(layer1)
        j = body.index("\n", i)
        body = body[:j + 1] + ARM_B_LAYER1 + "\n" + body[j + 1:]
    parts = "notes/(設計者注記)と mock/(モック)" + (" と ruled/(要求・仕様)" if has_ruled else "")
    head = (f"# 指示\n\nモックパッケージ= このファイルと同じフォルダの {parts}。読んでよいのはこのフォルダの中だけである。"
            "検査報告書をこのフォルダの report.md に書くこと。\n\n---\n\n")
    return head + body


def main():
    stage = Path(sys.argv[1]).resolve()
    stage.mkdir(parents=True, exist_ok=True)
    manifest = {"prompt_source": str(PROMPT_SRC.relative_to(BOMDD)).replace("\\", "/"),
                "prompt_sha256": hashlib.sha256(PROMPT_SRC.read_bytes()).hexdigest(), "packages": {}}
    order = [(i, s, a) for i in ITEMS for s in ("pre", "post") for a in ("A", "B")]
    for n, (item, state, arm) in enumerate(order, 1):
        product, states, notes, mocks = ITEMS[item]
        pcommit, ucommit = states[state]
        ui_repo, ui_commit = ("ViewPrismUI", ucommit) if ucommit else (product, pcommit)
        pkg = f"P{n:02d}"
        root = stage / pkg
        entries = []
        groups = [("notes", ui_repo, ui_commit, notes), ("mock", ui_repo, ui_commit, mocks)]
        if arm == "B":
            groups.append(("ruled", product, pcommit, RULED))
        for group, repo, commit, specs in groups:
            for path in expand(repo, commit, specs):
                raw = git(repo, "show", f"{commit}:{path}")
                note = None
                if group == "mock" and path.endswith(".html"):
                    raw, note = reduce_standalone(raw)
                dest = root / group / Path(path).name
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(raw)
                entries.append({"file": f"{group}/{dest.name}", "source": f"{repo}@{commit}:{path}",
                                "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw), **({"note": note} if note else {})})
        p = prompt(arm, arm == "B").encode("utf-8")
        (root / "prompt.md").write_bytes(p)
        manifest["packages"][pkg] = {"item": item, "state": state, "arm": arm, "files": entries,
                                     "prompt_sha256": hashlib.sha256(p).hexdigest(),
                                     "total_bytes": sum(e["bytes"] for e in entries)}
    (HERE / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n", encoding="utf-8",
                                        newline="\n")
    for pkg, v in manifest["packages"].items():
        sys.stdout.write(f"{pkg} {v['item']} {v['state']} {v['arm']} files={len(v['files'])} bytes={v['total_bytes']}\n")


if __name__ == "__main__":
    main()
