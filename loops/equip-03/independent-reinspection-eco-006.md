# ECO-006 独立是正確認検査報告(Codex fresh・read-only・2026-08-02・対象= 8a874ea..e876e81)

- 検査官: GPT-5(Codex・配備モデル ID= unknown〔自己申告〕)・fresh セッション(codex exec 直接)
- 検査条件: read-only・HEAD= e876e81・worktree clean を検査官が自己確認・書込みを伴う再実行なし
- 検査官報告(判定部・無改変転記):

## 所見別判定

| 所見 ID | 判定 | 理由(要旨) |
|---|---|---|
| IA-01 | **CLOSED** | 鋳造 unit は packages/*/dist/ に限定・package 定義は M-PKGDEF-015/016 に分離済み。残余(tsbuildinfo 混載)は artifact.type と notes に明記= **宣言済み境界と現物一致 — 境界を理由とする不合格扱いはしない**(境界受理) |
| IA-02 | **CLOSED** | M-SCHEMA-013 は schemas/ref-v0/ へ縮小・plm-*.schema.json 3 件は M-SCHEMA-CONTRACT-014 に分離。実ディレクトリ構成と一致 |
| IA-03 | **PARTIAL** | 指摘分(viewer→core・CI→build/pkgdef)は補完・意味論も明文化。ただし 61 自身が同意味論なら M-CLI-005→BUILD-CORE/VIEWER・M-CORE-GRAPH-002→M-SCHEMA-013 が必要なのに未追記と認めている= 全面解消せず |
| IA-04 | **CLOSED** | 論拠を「製造帰属が違う」へ訂正済み・routing/work-order 実文言と一致 |
| IA-05 | **CLOSED** | §5 追記で段階区別+revision/コマンド固定。8a874ea= 5 ファイル変更も検査官が確認 |

## New 所見

| ID | 等級 | 内容 | 帰属 |
|---|---|---|---|
| NEW-ECO006-01 | medium | order §5 が「是正後の受入は本 order 末尾へ追記」と宣言したまま、e876e81 最終個体の受入記録が order に存在しない(宣言未履行)。61 §7.2= 工場段階 info 179 / commit message= 台帳追随後 176 の段差も order 上未固定 | **設計者(fable)** |

(61 末尾の `</content>` 混入は 8a874ea 時点で既存のため new に数えない、と検査官が明記)

## 総合判定

**REJECT**(IA-03 PARTIAL+NEW-01)。他 4 件 CLOSED・宣言済み tsbuildinfo 境界は現物一致。

## 主観察者の突合(2026-08-02)

- IA-03 PARTIAL: **CONFIRMED** — 工場の 61 §7 の自認と整合。処置= 差戻 2 回目(既存 unit への
  変更を depends_on 追加行のみに限定して許可・検算根拠必須・基準の一貫適用)。
- NEW-01: **CONFIRMED** — 設計者帰属(fix2 commit 時に order 末尾の受入追記を怠った)。
  処置= 設計者是正(fix3 で order §5 へ最終受入記録を追記)。
- 通算(equip-03 独立検査): 初回 5 提起+再検査 new 1 提起= **6 提起 6 CONFIRMED・誤検出 0**。
  境界受理 1 件(tsbuildinfo — 宣言済み残余を再提起せず現物一致検査で受理)= 境界受理の 2 例目
  (ECO-024 BOUNDARY-DUP に続く・別ベンダー継続でも成立)。
- 61 末尾 `</content>` 混入の観測: 検査官指摘のとおり 8a874ea 由来 — fix3 で除去(衛生)。
