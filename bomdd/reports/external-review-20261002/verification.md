# 外部レビュー(2026-10-02)の照合と裁定 — 2026-10-03

- 原文: [review.md](review.md)(.docx からの写し)。対象コミット= `069e0d5`(照合時の HEAD と同一)。
- 照合者: claude-fable-5-1(EQ-001)・Claude Code。照合は原文の根拠リンクの行を実読し、実装欠陥 2 件は手元で再現または読解した。
- 裁定: user 2026-10-03 DECIDE「1:A 2:A」— 1= レビューの目標モデル(保守性要求を上流 S-BOM として人が先に裁定・E-BOM は利用者に意味のある機能で切る・
  承認済み E/S 版から統括 AI が M-BOM / Control Plan を導出)を採用し 1 機能で試行 / 2= 検査器の偽陰性 2 件と文書矛盾 2 件を今すぐ起票(修正 ECO 2 本+文書 ECO 1 本)。

## 論点ごとの照合

| 論点 | レビューの主張 | 照合の方法 | 結果 | 行き先 |
|---|---|---|---|---|
| 1(P1) | S-BOM が Phase 6 にあり、保守性要求を E/M の構造決定前に承認する入力が無い | playbook §1 工程表・53 テンプレ・s-bom-template §交換コスト を実読 | 工程表どおり(Phase 6 に As-Built と並置)。目標モデルの採否は user 裁定 1 | 裁定 1:A → ECO-094(試行) |
| 2(P1) | 粒度規準が playbook では candidate、phase3 では留保なし | playbook §4.1 L114 と phase3-design.md L6 を比較 | 一致: playbook「粒度規準(candidate)」/ phase3「**粒度規準**: 部品は…」(candidate の語なし) | 文面の逸脱= ECO-093 / 方針= ECO-094 |
| 3(P2) | 非 GUI CAD の共通入口が無い(CLI 実証は既知) | loops/cli-cad-01/report.md の留保を確認 | 既知(OBS/EXP の新設なし) | 記帳のみ(本節) |
| 4(P2) | G3・phase3・phase4 は 20/30〜34/40、40-work-order は UI-CAD で 35 必須 | 列挙箇所を grep(method/ 配下 15 箇所) | 一致。35 の条件を持つのは 40-work-order・templates/README・developer-navigation・00-charter の側のみ。G3・phase3・phase4・34-routing・bomdd-next は 35 を欠く | ECO-093 |
| 5(P1) | 規範→実行証拠の接続不足は既知(ECO-086/090) | improvements.md OBS-20261002-01・ECO-090 §0.2 | 既知 | 記帳のみ(ECO-094 の追跡項目に含める) |
| 6(P2) | EXP-20261002-01 の主指標 0/3 を「使われない」と読めない | improvements.md L8245 の文を実読 | 文はそのとおり(「0/3 なら…見直す材料にする」) | 補助注記の追記(主指標は不変・本 ECO 群の記録 commit で) |
| 7(P2) | コンテキストの範囲・寿命は観測が先 | OBS-20261002-03 | 既知(着手条件が記帳済み) | 記帳のみ |
| 8(P2) | C9 は TRX があれば行単位の判定のみで、終了コードも ResultSummary も見ない | self-conformance.py L1164〜1181・L1092〜1118 を実読 | 一致(読解)。`p.returncode` は trx 不在のときだけ参照・`ResultSummary`/`RunInfos` の参照 0 件 | ECO-091 |
| 9(P2) | witness は skip-worktree 付き entry を一時 index へ引き継ぎ、作業ツリーの bytes でなく index の bytes を証明する | 隔離リポで再現([witness-skip-worktree-repro.sh](witness-skip-worktree-repro.sh)) | **再現**: 不正 YAML を index に置き skip-worktree → 作業ツリーは正常 YAML → witness tree の blob= index の不正 YAML。対照(フラグなし)= 作業ツリー。実 index 不変。`git add` の戻り値も未確認(読解) | ECO-092 |
| P3 | README は playbook を正本と明記、playbook 冒頭は「単一題材検証済み・method-v1 と未統合」 | README L16・playbook L3〜5 を実読 | 一致 | ECO-093 |

## 限定子

- 論点 8・9 は合成入力での再現(各 N=1)。自然発生例は未観測。self-conformance 全体の PASS には影響していない(レビューも同旨)。
- 本リポの skip-worktree / assume-unchanged entry は照合時点で 0 件(`git ls-files -v | grep -c '^[Sh]'`)— 論点 9 への現時点の露出はない。
- C9 は CI(windows job・`--dotnet`)で毎 push 走る= 最終層の計器。witness はローカルのみ(C18・pre-push)。
- 論点 1・2 の「目標モデル」はレビューが置いた前提であり、リポからは検証できない — 採否は user 裁定 1 で決めた。

## 採らなかったこと

- 論点 3・5・6・7 の新規 OBS/EXP(既存の記録で覆われている — レビュー自身が「消費者のいない記録を増やさない」と述べる)。
- レビューの「最初に裁定 1 を決めてから修正へ」の順序 — 修正 3 件は目標モデルと独立なので待たない(user 裁定 2:A)。
