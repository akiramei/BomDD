# BomDD Reference Schema (ref-v0, draft) — 参照層の形式化

> **ステータス**: draft(検証対象であり規格ではない)。
> **スコープ宣言**: 本ディレクトリは BomDD 成果物の**参照層(reference layer)だけ**を形式化する —
> (1) ID の文法(どの品番ファミリーが存在し、どこで定義されるか)
> (2) 参照エッジ(どのファイルのどのフィールドが、どのファミリーの ID を指すか)
> (3) 参照整合の検査規則(リントルール)とゲートへの割付
>
> **意味論(semantic layer)は形式化しない。** フィールドの意味・語彙・構造の完全性は引き続き
> [../../schema-candidates-index.md](../../schema-candidates-index.md) の candidate 表であり、同 §5 の昇格条件を満たすまで硬化しない。
> 本スキーマの JSON Schema は全て `additionalProperties: true` / 最小 `required` で、**構造を縛らず参照だけを縛る**。

## 1. なぜ参照層だけ先に硬化するか(§5 との整合)

schema-candidates-index §5 は「早すぎる形式化=片ドメイン構造の焼き込み」を避けるため JSON Schema 化を保留した。
参照層はこの懸念の**外**にある:

1. **rule of three 到達**: 品番ファミリー(REQ/E/M/K/CP/S/…)と `*_refs` フィールドは、MoviePad・WebAPI・Saga・LibraryLending・ViewPrism2/UI の **N≥5** で同型のまま再出現した。テンプレ・バイアスではなく不変。
2. **不在のコストが実測された**: 参照整合が規律(人間)でしか保たれないことによる実害 — IR ロケーション2系統分裂・lineage 手動再帰属(テンプレ64)・UI-IR なし製造(ViewPrismUI ECO-022 CAPA)・PLM 試作のパーサ地獄(未凍結スキーマを手書きパーサが追跡)。
3. **意味論と独立**: ID 文法と参照エッジは「E-BOM に何を書くべきか」を一切固定しない。フィールドが増えても・語彙が変わっても、参照層は安定する。

この分離判断は index 側に追記済み(§7 addendum)。

## 2. 構成

| ファイル | 内容 |
|---|---|
| [id-grammar.draft.yaml](id-grammar.draft.yaml) | 品番ファミリーの台帳: 接頭辞・文法・定義サイト・厳格度 |
| [ref-edges.draft.yaml](ref-edges.draft.yaml) | 成果物ごとの ID 定義サイトと参照エッジ+リントルール台帳(R-*)とゲート割付 |
| [bomdd-ref.draft.schema.json](bomdd-ref.draft.schema.json) | 各 YAML/JSON 成果物の参照層 JSON Schema($defs 単位で適用) |

**正本の序列**: `id-grammar` と `ref-edges` が正本。JSON Schema はそこから導出された検査器向け表現であり、矛盾時は YAML 側が勝つ。

## 3. 設計原則

- **寛容な文法**: ID は「ファミリー接頭辞 + 非空の尾部」。尾部の採番方式(連番/意味名/複合)は縛らない。
  実例が根拠: `K-DESIGN`(無番号)・`CP-UI-G1`(golden 系)・`E-UI-BROWSE-022`(領域名入り)は全て合法。
- **厳格度は3段**: `strict`(定義サイトが機械可読 → 壊れ参照は error)/ `advisory`(定義が散文中 → warn)/ `reserved`(ファミリー予約のみ、定義サイト未運用)。
- **ゲート束縛**: リントルールは常時 error ではなく、playbook のゲート(G1/G3/凍結/受入/ECO)に割り付ける。
  draft 状態の BOM に完全性を要求しない(「重いから使わない」D1 対策)。
- **クロスリポ対応**: UI-CAD リポ(例 ViewPrismUI)と製造リポ(例 ViewPrism2)をまたぐ参照は
  `bomdd-workspace.yaml`(リポ集合の宣言。ref-edges §workspace 参照)を介して解決する。

## 4. 検証手順(draft の卒業条件)

1. **遡及リント**: ViewPrism2(41 E 品目・27 ECO)と BomDD-LibraryLending-Sample に対しリンタを走らせ、
   (a) 文法・エッジ定義が実物を false positive なしで受理するか (b) 既知の実害(IR 欠落・lineage 崩れ)を検出できるか を測る。
2. **PLM v0 の固定オラクル**として本スキーマを使用(既知欠陥を植えた fixture リポへの期待所見プロファイル一致)。
3. 2 プロジェクト以上で false positive 率が運用可能水準に収まったら `draft` を外し ref-v1 とする。
   実物と衝突したら**スキーマ側を直す**(実物が正、が draft 期間の規律)。
