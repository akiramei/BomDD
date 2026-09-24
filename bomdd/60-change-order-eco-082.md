# Change Order — ECO-082(handoff 実装規則の数値上限を外す — 本体「15 行程度」・DISCUSS の reasoning「3 点以内」・P7 の再掲/契約 v0.4 不変・F5 待機形は維持)

> 指示: user 2026-09-24「所見2も適用して」(/claude-api prompt-audit 所見 2)。契約 §1 は変えない。変えるのは §2 実装規則(交換可能・default)の 3 箇所。
> **起票と製造を同一 commit で行う**(文書のみ・ECO-076 の型)。受入は製造者較正のみ(当方の選択・ECO-076 と同じ文書のみの変更)。
> verified 昇格は self-conformance PASS と CI 結論を観測した後の受入 commit で(観測前に転記しない)。

## 担当設備(equipment)

- 起票・製造: requested/resolved `claude-opus-5-5`・Claude Code(Claude Agent SDK)・来歴 **self-reported**
- producer: EQ-004
- 独立検査: なし(文書のみ・製造者較正のみ。inspector 行は置かない)
- 設備台帳: 本 ECO で EQ-004(claude-opus-5-5 @ claude-code・unqualified)を登録する(EQ-001 は claude-fable-5-1 で、同一設備として記述すると model 軸が偽になる)。

## 0. 実測(起票根拠)

- **監査所見**(2026-09-24・/claude-api prompt-audit・基準モデル Claude Opus 5.5): `handoff.md` §2.2 共通「パケット本体は 15 行程度」・§2.2 DISCUSS「reasoning は 3 点以内」・
  §2.3 P7「(本体 15 行程度)」は、出力を数値で縛る書き方(監査手引きの「出力整形の振り付け」型)に当たる。数値の上限は冗長な旧モデルに合わせた縛りで、現行モデルでは
  難しい論点の推論を削る側に効く。同じ趣旨は読み手規則 3(本文は判断に必要な事実だけ・証拠は付録か記録へ)が数値なしで既に述べている。
- **既存裁定との照合(実読)**: ECO-076 §1「採らない」は「本文行数の structural 上限(15 行「程度」のまま — 硬い上限は待機形・REQUEST 様式と衝突し、証明のための複雑性になる)」—
  硬い上限を入れない判断であって、「程度」の数値を残す理由は書かれていない。本 ECO は硬い上限を足さず、数値の目安を外す(同じ方向)。
- **残すもの**: §2.3 F5「待機形: ヘッダ+2 行以内」と §2.2 待機形の「1〜2 行のみ」— structural 検査(機械判定・送信停止)の形式要件であり、数値を外すと structural から semantic に
  移ってしまう。options「2〜4 個」— 長さでなく選択肢の設計(契約が実装側に置いた個数の default)。

## 1. 変更要求(凍結・文書のみ)

1. `method/templates/product-profile/skills/handoff.md` §2.2 共通: 「パケット本体は 15 行程度。」→「パケット本体は判断に必要な事実だけに絞る。」
2. 同 §2.2 DISCUSS: 「reasoning は 3 点以内。」→「reasoning は thesis を実際に支える点だけ。」
3. 同 §2.3 P7: 末尾の「(本体 15 行程度)」を削る。
3b. 同 §3 DISCUSS の例: 「reasoning: (3 点以内)」→「reasoning: (thesis を支える点)」(製造中の発見で追加 — §4 参照。例は規則より強く出力の形に効くため、規則と例を食い違わせない)。
4. `.claude/skills/handoff/SKILL.md` を正本と同期(同じ 3 箇所・既知 3 hunk は不変)。
5. `bomdd/70-equipment.yaml` に EQ-004 を登録。`method/improvements.md` に本節+EXP-20260924-01(効果の計測)。

**採らない**: 契約 §1 の変更 / F5・待機形の行数(structural 検査の形式要件)/ options の個数 / 本文長の新しい検査(機械・semantic とも)/ 他の所見(3・factory-delegate)の同乗。

## 2. 影響なし予測(製造前・凍結)

diff= skills 正本・写し・70-equipment.yaml・improvements.md+台帳系(order・register)のみ。契約 §1 の本文は不変(sha256 で確認)・core 固有語 0 を維持(ECO-075 V1 の 13 語)・
写しと正本の差= 既知 3 hunk のみ・C7 13 本不変・tools/templates(60-change-order)/hooks/.github diff 0・worklist 新規 ID 1(EXP-20260924-01)・警告 0。

## 3. 受入条件(製造前に凍結・二部形)

- V1(条件): 正本と写しの両方で `15 行程度` と `3 点以内` が 0 件、`判断に必要な事実だけに絞る` と `thesis を実際に支える点だけ` が各 1 件、F5 行に `2 行以内` が残っていること — 検査法: grep。
- V2(条件): 契約 §1(```text ブロック先頭の HANDOFF CONTRACT v0.4)の sha256 が変更前後で一致し、core(adapter 見出しより前)の固有語が 0(13 語)で、写しと正本の差が既知 3 hunk のみであること — 検査法: sha256・grep・diff。
- V3(条件): self-conformance 全 PASS(exit 0 観測後に commit)・CI success・diff 窓= allowed_paths のみであること — 検査法: 単一入口・`gh run list --commit <full sha>`・`git diff --stat baseline..head`。
- V4(条件): 製造者較正のみ・較正 receipt(trigger ①: verified 昇格)があること。
- V5(条件・クローズ条件でない): 効果は EXP-20260924-01 で測ること。

## /preflight receipt(起動経路: **job 経由** — `bomdd-job.py ECO-082` の出力を開始 artifact として読んだ)

- 分類= 既裁定の適用実装(user 指示「所見2も適用して」・契約は不変)。baseline `20b18bb`= **confirmed**(作業木 clean・push 済み)/ 次番 082= **confirmed**(register に id 0 件)/
  変更対象 3 箇所= **confirmed**(実読・正本と写しで同文)/ ECO-076 の「採らない」の実文= **confirmed**(§0 に引用)/ 同一ファイルへの進行中 ECO がないこと= **confirmed**(進行中は ECO-079〔implemented〕のみで、その allowed_paths は handoff.md・写し・70-equipment.yaml・improvements.md を含まない。handoff.md を窓に持つ ECO-075/076 は verified)。
- discovered(推測・契約外): 製造者の設備が台帳に無い(EQ-001 は claude-fable-5-1)= **confirmed**(実読)→ §1-5 で EQ-004 を登録。
- 開始判定: **PROCEED**・override 0。

## 4. 製造と受入の実測(2026-09-24・同一 commit)

- 製造物: 正本 §2.2 共通・§2.2 DISCUSS・§2.3 P7・§3 DISCUSS 例の 4 箇所 / 写し(同じ 4 箇所)/ 70-equipment.yaml に EQ-004 / improvements.md 節+EXP-20260924-01。
- **製造中の発見(1 件・commit 前に変更要求へ追加)**: V1 の grep で `3 点以内` が §3 の DISCUSS 例(`reasoning: (3 点以内)`)に 1 件残った。監査所見 2 は §2.2・§2.3 だけを
  挙げており、例を見落としていた(監査の被覆漏れ)。規則だけ外して例に数値を残すと、例の方が強く出力の形を決める — §1-3b として追加した。起票と製造が同一 commit のため、
  凍結後の変更ではない(order の初版に含めて commit する)。
- **V1**= PASS(観測: 正本・写しとも `15 行程度` 0・`3 点以内` 0・`判断に必要な事実だけに絞る` 1・`thesis を実際に支える点だけ` 1・`F5 待機形: ヘッダ+2 行以内` 1)。
- **V2**= PASS(観測: 契約 §1 の sha256 `3480569a6454` が変更前後で一致・64 行 / core〔adapter 見出しより前〕の固有語 0 / 写しと正本の diff 出力が変更前と byte 一致)。
- **V3**= §5 で記録(観測後)。

## 5. クローズ(2026-09-24・verified・製造者較正のみ)

- **V3**= PASS(観測: 変更を stage してから self-conformance を実行 → **exit=0 全 PASS**〔C16 order 50 件・C17 40 件〕→ witness(tree 7e6170216b4a・gates 1・producer EQ-004)→
  入口 dry `ADVANCE ECO-082 OK` → 製造 commit a3356eb → push → CI run 35952158670 **success**)。diff 監査の窓: baseline `20b18bb` → head `a3356eb`(**窓閉鎖**・受入 commit は台帳系のみ)。
  窓内= allowed_paths の 6 ファイルのみ(`git diff --stat 20b18bb..a3356eb`)。
- **V1/V2**= §4(PASS)。**V4**= 製造者較正のみ(独立検査なし)・下の較正 receipt。register: `implemented → verified`・head 凍結。
- **V5(非クローズ条件)**: EXP-20260924-01 で次の handoff 20 通を数える。本 ECO の handoff(製造報告・受入報告)自体が最初の適用個体。
- 実測(正直記載): self-conformance は 1 回目で PASS(ECO-076 で 3 例目だった「stage 前実行で C13 偽 FAIL」は、先に stage して回避)。入口の最初の dry は witness 未生成で
  `UNMEASURABLE WITNESS_UNREADABLE`(exit 2)— 手順の順序(witness produce が先)を運転員が飛ばしたもの。produce 後に ADVANCE。

### 較正 receipt(/calibrate 自己適用 — trigger ①: verified 昇格・receipt_author_role= producer。文書のみの変更)

- 査定した主張と判定:
  1. 「正本と写しから数値上限の語(`15 行程度`・`3 点以内`)が消え、置換文が各 1 件あり、F5 の行数は残っている」— **observed / 適格**(grep・V1)。
  2. 「契約 §1 は不変」— **observed / 適格**(契約ブロックの sha256 `3480569a6454` が変更前後で一致・64 行)。
  3. 「core は環境非依存のまま・写しは正本と同期」— **observed / 適格**(core 固有語 0・写しと正本の diff 出力が変更前と byte 一致)。
  4. 「数値目安を外しても本文は膨らまず裁定点を落とさない」— **unknown(未測定・EXP-20260924-01)**。
- 検出した計器欠陥(帰属つき): 製造物 0 件。上流(監査)1 件 — 監査所見 2 が §3 の例に残る同型の数値を挙げていなかった(被覆漏れ)。V1 の grep が捕捉し、製造内で是正した。
  受理側の手順 1 件(witness 生成前に入口を dry 実行 — 計器は正しく「読めない」と言っており計器欠陥ではない)。
- 検出力の限界: V1 は文字列の有無しか測らない — 言い換え後の文が同じ意図を伝えるかは読解。効果は未測定。独立検査なし。数値目安の有無が実際の handoff の長さに与える影響は
  EXP-20260924-01 の外部計測(人間の指摘回数)でしか観測されない。
- battery 行別記録:

  | Q | asked/NA | 判定 | 実測 or 読解 | 所見 |
  |---|---|---|---|---|
  | Q1 | asked | observed/適格 | 実測 | grep・sha256・diff(V1/V2)。検査文(order §3 の条件)は grep が測る範囲に限っている |
  | Q2 | asked | NA 相当 | — | 文書変更に known-bad 対照なし(宣言)。V1 の grep は製造途中で `3 点以内` 1 件を実際に検出しており、陽性の実例にはなった |
  | Q3 | asked | observed/適格 | 実測 | 4 箇所それぞれを個別の grep で確認(1 つの一括一致に頼らない) |
  | Q4 | asked | observed/適格 | 実測 | 検査入力= 実ファイル(正本・写し)そのもの。宣言 fixture なし |
  | Q5 | asked | observed/適格 | 実測 | 未測定(効果・独立検査)を unknown として分離 |
  | Q6 | asked | observed/適格 | 実測 | 検査 exit 観測 → witness → 入口 dry → commit → push → CI success(条件で結んだ順) |
  | Q7 | asked | NA | — | 陽性対照なし(文書) |
  | Q8 | NA | — | — | 免除機構なし |
  | Q9 | asked | observed/適格 | 実測 | witness(ECO-082.json・tree 7e6170216b4a)・commit a3356eb・CI run 35952158670 を同一個体として照合 |
  | Q10 | asked | 宣言 | 読解 | 上記「検出力の限界」 |
  | Q11 | asked | observed/適格 | 読解 | 入力クラス= 規則文(§2.2・§2.3)と例(§3)を分けて検査 — 例のクラスで漏れが出た |

- このクローズが支持しないもの: 数値目安を外した効果(EXP-20260924-01)/ 独立検査による確認 / 契約の変更(していない)/ 製品リポでの適用結果(kit 再設置まで非波及)。
