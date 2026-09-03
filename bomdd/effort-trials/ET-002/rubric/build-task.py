#!/usr/bin/env python3
"""ET-002 — 課題文 input/TASK.md を組み立てる(self-conformance.py の全文を HEAD から転写して埋め込む)。
run 開始前に 1 回だけ実行(init が hash を封印する)。来歴: 転写元 revision と sha256 を TASK.md 冒頭に記す。"""
from __future__ import annotations
import hashlib, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TRIAL = HERE.parent
ROOT = TRIAL.parents[2]
SRC = ROOT / "method" / "tools" / "self-conformance.py"
sys.stdout.reconfigure(encoding="utf-8")

HEAD = """# 課題: 検査スクリプトの全ゲートについて「走査母集団が空のときに無音で PASS する」箇所を洗い出す

以下は BomDD リポジトリの自己適合検査 `method/tools/self-conformance.py` の全文です(転写元 revision `{rev}`・
sha256 `{sha}`)。この中には `check("Cxx", ok, msg)` で判定を出すゲートが複数あります。

## 定義

- **走査母集団**: そのゲートが検査のために列挙・走査する対象の集合(例: YAML ファイル群・台帳の entry 群・
  リンク群・fixture 群・test project 群)。ゲートによっては複数の母集団を持ちます。
- **無音で PASS(SILENT)**: ある走査母集団が **0 件** のとき、そのゲートが (a) FAIL / UNKNOWN にならず、かつ
  (b) PASS 行のメッセージに母集団の件数(数字、または空リストの表示)が出ない、という条件を両方満たす。
  つまり「何も検査していないのに、検査したように見える」状態です。
- **OK**: 母集団が 0 件のとき FAIL/UNKNOWN になる(ガードがある・陽性対照が母集団に依存して落ちる)、または
  PASS するがメッセージに件数(0 件・`[]` 等)が表示される、または走査母集団を持たない固定操作のゲート。

判定は**コードに書かれている振る舞い**だけで行ってください。「現実には 0 件にならない」という理由で OK に
しないでください(構造としてどう振る舞うかを問うています)。ゲートが複数の母集団を持つ場合、**いずれか 1 つでも**
SILENT の条件を満たせばそのゲートは SILENT です。

## 対象ゲート(この ID で回答してください)

C1, C2, C3, C4, C5a, C5b, C6a, C6b, C7, C8, C9, C10, C11, C11b, C12, C13, C14, C15, C16, C17, C18

## 出力形式(厳守)

最終回答の本文に、ゲートごとに **1 行ずつ**、次の形式で書いてください(行頭から・判定語は大文字):

    C1: OK — <母集団と根拠を 1 行>
    C3: SILENT — <母集団と根拠を 1 行>

同じゲートについて相反する判定行を書かないでください。判定行以外の説明を添えても構いません。

## 検査スクリプト全文

===== BEGIN method/tools/self-conformance.py =====
{src}
===== END method/tools/self-conformance.py =====
"""


def main() -> int:
    rev = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    src = SRC.read_text(encoding="utf-8")
    sha = hashlib.sha256(SRC.read_bytes()).hexdigest()
    out = TRIAL / "input" / "TASK.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(HEAD.format(rev=rev, sha=sha, src=src))
    print(f"wrote {out} ({out.stat().st_size} bytes) src={sha[:12]} @ {rev[:7]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
