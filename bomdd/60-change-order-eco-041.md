# Change Order — ECO-041(独立検査の判定語意味論・報告様式・集計引用規則の明文化)

> 裁定: user 2026-09-01(第 3 回較正掃引の gate)「D1+D3+R1 を一つの軽量 ECO として採択」—
> 6 条件つき(下記 gate ① 節)。出典= /calibrate 第 3 回掃引(題材= 独立検査官〔AI judge〕・
> EXP-20260831-04 第 3 回観測)の declaration deficiency 2 件+reference-truth deficiency 1 件。

## 担当設備(equipment)

- 査定・製造:
  - requested: `claude-fable-5`
  - resolved: `claude-fable-5`
  - ハーネス: Claude Code(Claude Agent SDK)
  - 来歴: **self-reported**

## 0. 実測(起票根拠 — 掃引 ③ 第 3 回の所見)

- **D1**: REJECT の意味論が明文定義されていない — 実文(4 レポート)は一貫して工程語
  (「製造前凍結不可」「line-ready 未達」「受入不能」)であり、register も REJECT 後の
  verified を「起票時凍結の受入基準に対する判定」として維持してきたが、この読みは
  どこにも規定がなく「製品不良の証明」と誤読可能だった。
- **D3**: 限界節・遵守申告の様式が第 4 ラウンド(`independent-reinspection-eco-019.md`
  §4〜5)のみ — 第 1〜3 ラウンドには無い。
- **R1**: 真正判定の集計「30 提起・30 CONFIRMED・誤検出 0」は事実だが、接地方法
  (実プローブ 17 / コード読解 13)と留保 3+限定 2 を圧縮しており、**単独引用は検査官の
  精度一般の根拠として不適格**(gate 裁定 6 — 査定者自身の引用を Q1 が捕捉した自己捕捉を
  第 3 回の**主要観測**として扱う。improvements.md の「副次」表記はこの裁定で主要へ格上げ —
  記録は append-only につき本 order に記す)。

## gate ①(製造承認)

**承認 2026-09-01 maintainer** — 6 条件: ①D1+D3+R1 を一括採択(REJECT= process decision
明文化 / 報告標準様式に限界+遵守申告 / 集計引用は evidence class+留保併記・単一精度指標へ
圧縮しない)②**前向き適用のみ** — 過去 ECO・検査報告の歴史的記録は書き換えない ③clean
known-good 特異度・同一対象再測定・他ベンダー比較は今回対象外(次回検査機会の測定候補)
④calibrate battery は変更しない(reference-truth deficiency は既存 battery で検出できており
新規 Q の追加根拠としない)⑤EXP 第 3 回は 5 分類の分離記録(合算しない — 記帳済みと一致)
⑥自己捕捉を主要観測として残す。

## 1. 変更要求(製造対象)

`method/bomdd-playbook-v1.md` §4.4 の「高リスク検査治具の異系統独立受入検査」段落へ追補
1 節(判定語の意味論と報告様式)— REJECT= process decision / 報告に限界+遵守申告 /
集計引用の evidence class+留保併記規則 / **前向き適用の明文**。既存文は無変更(append のみ)。

## 2. 影響なし予測(反証可能・製造前に凍結)

- diff は `method/bomdd-playbook-v1.md` の §4.4 追補+台帳系のみ。既存文・過去レポート・
  register の歴史的記録は無変更。C13(リンク)判定不変(追補にリンクなし)。C16 は本 order を
  required と判定する見込み — receipt 埋め込み済み。

## 3. 受入(起票時凍結)

- **V1**: 追補が append のみであること(diff で §4.4 既存行の変更ゼロ)。
- **V2**: `self-conformance` 全検査 PASS・既存判定不変。
- **V3**: push 後 CI 緑(headSha 照合)。
- **V4**: diff 窓が §2 の範囲に収まる。
- 較正: 散文規則につき機械対照なし(ECO-036/038 と同じ正直宣言)— 遵守は次回の独立検査
  報告・集計引用の実運用で観測する。

## /converge receipt(本追補の設計に適用 — 起動経路: 人間裁定〔D1+D3+R1 採択〕)

- **判定: 収束**(round 軌跡: 2→0→0)。
- 周回数と新規指摘: round 1 = 2 件(前向き適用の明文を追補自体に内蔵 — 裁定 2 を散文で
  再委任しない / 「verified 維持と両立」の理由説明を 1 文追加 — 過去運用の再解釈でなく
  説明である形に限定)/ round 2 = 0 / round 3 = 0。
- 検証した主張(要点): 4 レポートの判定語実文・register の verified 維持文言・第 4 ラウンド
  限界節/遵守申告の実在(掃引 ③ で全数実読済み)/ §4.4 該当段落の挿入位置と既存文の非変更。
- 未収束事項: なし。

## 4. 製造と受入の実測(2026-09-01)

- diff 監査の窓: baseline `3d55fcd`(起票直前 HEAD・起票+製造は同一窓)→ head は受入時に確定。
- §4.4 追補を §1 のとおり適用(append のみ)。
- 実測結果は §5 に追記する。

## 5. CI 実測

(push 後に追記)

## 6. クローズ

(受入後に追記)
