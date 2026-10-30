"""EXP-20261030-03 - build the deriver packages (definitions.md sections 2-3, 5.1).

Usage: python packages.py <staging-dir>
Reads every input with `git show <commit>:<path>` (never a working tree), writes T01-T06 under <staging-dir>, and writes
manifest.json next to this file (each staged file with its source and SHA-256). Refuses (exit 2) a required file that does not
exist at its commit.
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPOS = HERE.parents[3]
PRODUCT = "ViewTube"
MOCK = "bomdd/ui/mock/viewtube-v1.html"
NOTES = ["bomdd/ui/design-intent.md", "bomdd/ui/unresolved-questions.md", "?bomdd/ui/videos-cad.md"]
RULED = ["bomdd/10-requirements.yaml", "bomdd/20-spec.md"]

# package: (item, state, ViewTube commit); the order is definitions.md section 3
PACKAGES = {"T01": ("D1", "pre", "ad8c37c"), "T02": ("D1", "post", "6f24075f"),
            "T03": ("D2", "pre", "2060849"), "T04": ("D2", "post", "b9f629d6"),
            "T05": ("D3", "pre", "05e2d905"), "T06": ("D3", "post", "1cd3e7a5")}

ACTION = re.compile(r'data-ui-action="([^"]+)"')

PROMPT = """# 指示

このファイルと同じフォルダにあるのは、ある製品の設計の入力である。

- ruled/ — 要求(10-requirements.yaml)と仕様(20-spec.md)
- notes/ — UI の設計者注記
- mock/viewtube-v1.html — UI モック(HTML のソースとして読む)
- actions.txt — モックの `data-ui-action` の値の一覧(機械抽出・1 行 1 個)

読んでよいのはこのフォルダの中だけである。

## してほしいこと

入力が述べている**操作**を、下の形の表(JSON)へ**書き写す**。レビュー・欠陥の指摘・修正・提案はしない。
入力が何も言わない欄は推測で埋めず、`null`(availability は `not_drawn`)と書く。

```
{"states": [{"id": "...", "name": "...", "source": "mock" | "text" | "both", "selection_possible": true | false | null, "evidence": "..."}],
 "entities": [{"id": "...", "name": "...", "evidence": "..."}],
 "operations": [{"id": "...", "label": "...", "entity": "<entities の id>", "kind": "...", "mock_action": "<actions.txt の値>" | null,
                 "text_refs": ["REQ-... / 仕様の節"], "owner_surfaces": ["..."], "counterpart": "<operations の id>" | null,
                 "availability": {"<states の id>": "enabled" | "disabled" | "absent" | "not_drawn"}}]}
```

- **states** — モックが描く状態(キャプチャの引数・画面・モード)と、要求・仕様が名指す状態の和。`source` はどちらが述べているか。
  `selection_possible` = その状態で項目を複数選択できるかを入力が述べていれば true / false、述べていなければ null。
- **entities** — 操作の対象になるもの(データの種類)。
- **operations** — 利用者が行う操作。1 つの操作に 1 行。
  - `kind` は create, delete, assign, unassign, add, remove, archive, restore, update, navigate, view, other のどれか。
  - `mock_action` = モックでその操作を描いている `actions.txt` の値。モックが描いていなければ `null`。
  - `text_refs` = その操作を求める・前提にする要求の id と仕様の節。無ければ `[]`。
  - `owner_surfaces` = その操作を行う画面・領域。
  - `counterpart` = その操作を取り消す操作の id。入力に無ければ `null`。モックの操作名・表示文言も入力であり、そこから読める
    取り消しの関係は「入力にある」に数える。
  - `availability` = states の**すべての** id について、その状態でその操作が使えるか。
    enabled = 使える / disabled = 見えるが使えない / absent = 入力がその状態では無いと述べる / not_drawn = 入力が何も言わない。
- `actions.txt` のすべての値を、どれかの操作の `mock_action` に置くこと(製品の操作でないと判断したものは kind を other にする)。

## 出力

表をこのフォルダの table.json に書くこと。最後のメッセージにも、同じ表を 1 個の ```json ブロックとして含めること。
"""


def git(*args):
    return subprocess.run(["git", "-C", str(REPOS / PRODUCT), *args], capture_output=True, check=True).stdout


def exists(commit, path):
    return subprocess.run(["git", "-C", str(REPOS / PRODUCT), "cat-file", "-e", f"{commit}:{path}"],
                          capture_output=True).returncode == 0


def actions(mock_text):
    """definitions.md section 3: distinct data-ui-action values minus template literals and the drawing tool."""
    return sorted({a for a in ACTION.findall(mock_text) if "$" not in a and "{" not in a and not a.startswith("PreviewCad")})


def main():
    stage = Path(sys.argv[1]).resolve()
    stage.mkdir(parents=True, exist_ok=True)
    prompt = PROMPT.encode("utf-8")
    manifest = {"prompt_sha256": hashlib.sha256(prompt).hexdigest(), "packages": {}}
    for pkg, (item, state, commit) in PACKAGES.items():
        root = stage / pkg
        entries = []
        for group, specs in (("ruled", RULED), ("notes", NOTES), ("mock", [MOCK])):
            for spec in specs:
                path = spec.lstrip("?")
                if not exists(commit, path):
                    if spec.startswith("?"):
                        continue
                    sys.stderr.write(f"UNMEASURABLE: {PRODUCT}@{commit}:{path} missing\n")
                    sys.exit(2)
                raw = git("show", f"{commit}:{path}")
                dest = root / group / Path(path).name
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(raw)
                entries.append({"file": f"{group}/{dest.name}", "source": f"{PRODUCT}@{commit}:{path}",
                                "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)})
        acts = actions(git("show", f"{commit}:{MOCK}").decode("utf-8"))
        raw = ("\n".join(acts) + "\n").encode("utf-8")
        (root / "actions.txt").write_bytes(raw)
        entries.append({"file": "actions.txt", "source": f"derived from {PRODUCT}@{commit}:{MOCK}",
                        "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw), "count": len(acts)})
        (root / "prompt.md").write_bytes(prompt)
        manifest["packages"][pkg] = {"item": item, "state": state, "commit": commit, "files": entries}
    (HERE / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n", encoding="utf-8",
                                        newline="\n")
    for pkg, v in manifest["packages"].items():
        sys.stdout.write(f"{pkg} files={len(v['files'])} actions={v['files'][-1]['count']}\n")


if __name__ == "__main__":
    main()
