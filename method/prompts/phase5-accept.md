# Phase 5 — 受入・収束(設計者 AI への指示)

典拠: `method/bomdd-playbook-v1.md` §6。入力: 各工場の成果物 + `41-fixed-oracle.yaml` + `42-exploratory-probes.yaml`。

## 0. 不具合指摘時の初動規律
受入中、またはユーザー確認で成果物の間違いを指摘された場合、**直接ソースを修正しない**。まず defect escape / nonconformance として記録し、どの上流成果物に欠陥が宿ったかを帰属する。

- `spec_omission`: 仕様に要求が無い。REQ/仕様を改訂し、E-BOM/M-BOM/Control Plan/Oracle を同期してから fresh factory で再製造。
- `bom_sync_gap`: 仕様にはあるが BOM/工程/受入に落ちていない。該当 BOM を同期して再製造。
- `oracle_gap`: 仕様/BOMにはあるが検査が無い、または深さ不足。オラクル・ファーストで検査を追加/較正してから再製造。
- `design_system_part_missing`: CAD が要求する Card / CTA / Chip / Badge / IconButton 等が E-BOM/K-BOM/Design System BOM に無い。35/30/31/33 を同期して再製造。
- `design_system_not_applied`: design system 部品はあるが対象 surface への適用 matrix が無い。35 coverage_matrix と 30 display_contract_refs を補正。
- `display_contract_gap`: CAD に見える情報・値・範囲・件数・凡例が display contract / Control Plan に落ちていない。20/30/33/41 を補正。
- `manufacturing_miss`: BOM と検査は十分だが工場が外した。工場能力または製造不適合として扱い、fresh factory で再製造。
- `harness_bug`: 検査器側の誤判定。治具を修正・セルフテスト/較正し、既存測定値を再評価。

緊急封じ込めとしてソースを触る場合は、その事実を明示し、正式是正とは区別する。正式是正は上流成果物へ逆流し、改訂 BOM から再製造されて初めて完了する。

## 1. 測定
1. **固定オラクル実行**: 各成果物に固定シナリオを流し、**仕様由来の期待値**と突合(原版が無いので 2-way diff ではない)。等価規則に従い、付随表現(JSON 形状・キー綴り・ID 具体値)を差分に数えない。検査器が表現に過剰結合した疑いがあれば、それは**検査器側のずる**として別記録(side: harness。製品差分に混ぜない)。
2. **視覚ギャップ分析(UI-CAD 案件)**: `43-visual-gap-analysis.md` を作り、CAD(HTML mock + UI-IR + UI-BOM + Design System BOM)と実機を突合する。S1/S2 は cosmetic ではなく blocker。Card / CTA / Chip / Badge / IconButton が素の panel/text/button に退化していないかを見る。推奨は golden-in-the-loop: 反復ごとに実機スクリーンショットを CAD(M1/M2/M3 等)と突合し、S1 を先にゼロへ近づける。
3. **探索プローブ実行**: exploratory 次元の値を採取(多工場なら分散、1工場でも値を記録)。
4. **差分帰属**: 各差分・ユーザー指摘を `unspecified_bom_residue / specified_contract_miss(工場能力) / exploratory_unspecified_surface / observer_*` と、必要に応じて §0 の `spec_omission / bom_sync_gap / oracle_gap / design_system_part_missing / design_system_not_applied / display_contract_gap / manufacturing_miss / harness_bug` に分類。
5. **metrics**: `bomdd/52-metrics.yaml` に分解記録(raw 一致率単独で報告しない)。

## 2. ユーザーへの質問リスト(フォワード固有の還流)
ずる報告・探索層分散・unspecified_bom_residue を質問に変換してユーザーに提示する:
> 「工場は X を慣習で A と埋めました(他工場は B)。これは仕様として固定しますか?」
> 裁定: ①仕様に昇格(REQ/仕様/K-BOM へ追記) ②探索のまま(どちらでもよいと明文化) ③対象外

これがブレストで思いつけなかった要求を回収する第2の要求エリシテーション。裁定結果を cheat-log の「ユーザー裁定」欄に記録する。

## 3. 収束ループ
- 裁定で昇格した次元を BOM/K-BOM/仕様に反映する。オラクルへの昇格は**次ループの開始時のみ**(study 途中で固定オラクルに足さない)。
- `spec_omission` や `bom_sync_gap` は、仕様/E-BOM/M-BOM/Control Plan/Oracle の同期完了を確認してから次ループへ進む。同期前のソース直接修正で収束ループを開始しない。
- 補正した BOM を **fresh な工場**(前ループの成果・差分・cheat 非開示の新規サブエージェント)へ渡して再製造(Phase 4 をやり直す)。fresh であることが「修正がコーチングでなく BOM に宿った」ことの証明。
- **終了条件**: blocker 差分ゼロ かつ 新規 unspecified_bom_residue ゼロ(exploratory 宣言済みの分散は残ってよい)。
  UI-CAD 案件では S1 visual gap ゼロ、S2 visual gap が covered/out-of-scope 裁定済みであることも終了条件に含める。

## 4. 表現規律
全通過を「完全」と呼ばない。「**現固定オラクル被覆で未観測差分ゼロ**」と表現する。主張は常に「観測した範囲」。

終了したら Phase 6: `bomdd/50-as-built.yaml` を確定し、表面部品の Service BOM を `bomdd/53-service-bom.yaml`(テンプレ 53。概念と影響分析手順は `method/s-bom-template.md`)に書いて引き渡す。納品物 = 成果物 + `bomdd/` 一式(治具・オラクル込み——次の改修の回帰検査になる)。
