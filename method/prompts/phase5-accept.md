# Phase 5 — 受入・収束(設計者 AI への指示)

典拠: `method/bomdd-playbook-v1.md` §6。入力: 各工場の成果物 + `41-fixed-oracle.yaml` + `42-exploratory-probes.yaml`。

## 1. 測定
1. **固定オラクル実行**: 各成果物に固定シナリオを流し、**仕様由来の期待値**と突合(原版が無いので 2-way diff ではない)。等価規則に従い、付随表現(JSON 形状・キー綴り・ID 具体値)を差分に数えない。検査器が表現に過剰結合した疑いがあれば、それは**検査器側のずる**として別記録(side: harness。製品差分に混ぜない)。
2. **探索プローブ実行**: exploratory 次元の値を採取(多工場なら分散、1工場でも値を記録)。
3. **差分帰属**: 各差分を `unspecified_bom_residue / specified_contract_miss(工場能力) / exploratory_unspecified_surface / observer_*` に分類。
4. **metrics**: `bomdd/52-metrics.yaml` に分解記録(raw 一致率単独で報告しない)。

## 2. ユーザーへの質問リスト(フォワード固有の還流)
ずる報告・探索層分散・unspecified_bom_residue を質問に変換してユーザーに提示する:
> 「工場は X を慣習で A と埋めました(他工場は B)。これは仕様として固定しますか?」
> 裁定: ①仕様に昇格(REQ/仕様/K-BOM へ追記) ②探索のまま(どちらでもよいと明文化) ③対象外

これがブレストで思いつけなかった要求を回収する第2の要求エリシテーション。裁定結果を cheat-log の「ユーザー裁定」欄に記録する。

## 3. 収束ループ
- 裁定で昇格した次元を BOM/K-BOM/仕様に反映する。オラクルへの昇格は**次ループの開始時のみ**(study 途中で固定オラクルに足さない)。
- 補正した BOM を **fresh な工場**(前ループの成果・差分・cheat 非開示の新規サブエージェント)へ渡して再製造(Phase 4 をやり直す)。fresh であることが「修正がコーチングでなく BOM に宿った」ことの証明。
- **終了条件**: blocker 差分ゼロ かつ 新規 unspecified_bom_residue ゼロ(exploratory 宣言済みの分散は残ってよい)。

## 4. 表現規律
全通過を「完全」と呼ばない。「**現固定オラクル被覆で未観測差分ゼロ**」と表現する。主張は常に「観測した範囲」。

終了したら Phase 6: `bomdd/50-as-built.yaml` を確定し、表面部品の Service BOM を `bomdd/53-service-bom.yaml`(テンプレ 53。概念と影響分析手順は `method/s-bom-template.md`)に書いて引き渡す。納品物 = 成果物 + `bomdd/` 一式(治具・オラクル込み——次の改修の回帰検査になる)。
