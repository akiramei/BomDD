---
name: preflight
description: 作業開始条件の再認証(Task Contract + Revalidation・Phase 1)。既存状態に依存する作業(continuation・bug fix 等)の開始時に、task class ごとの最小契約(存在すべき前提)と現在確認できる状態を突合し、各前提を confirmed/missing/stale/contradicted/unknown で判定して、開始可否(PROCEED/PROCEED_WITH_LIMITS/HOLD/STOP)を preflight receipt 付きで出す。STOP は「現在の入力状態では正当に開始できない」という工程判定であり製品判断ではない。設計の収束(/converge)・証拠の資格査定(/calibrate)には使わない。
---

# /preflight — 作業開始条件の再認証(Task Contract + Revalidation・Phase 1)

> **本ファイルは写しである。正本は [`method/templates/product-profile/skills/preflight.md`](../../../method/templates/product-profile/skills/preflight.md)。**
> BomDD は `bomdd-init` の配布先ではないため、正本を置いても `.claude/skills/` には入らない。
> **同期規則**: 変更は必ず**正本側**へ入れ、本ファイルへ反映する(プレースホルダーは自リポ相対へ解決する)。
> 本ファイルだけを直接編集しない — 配布元と分岐すると、どちらかが必ず腐る。
> 由来: ECO-042(D-1 前例= ECO-032 の踏襲)。

正典: `method/templates/product-profile/skills/preflight.md`(本ファイルの配布元)。
関連: `/converge`(採用の収束)・`/calibrate`(証拠の資格査定)・
`method/bomdd-playbook-v1.md` §8.5(境界統制)。

目的: 「この作業を、**いま実際に利用可能な状態**から正当に開始・継続できるか」を開始前に
判定する。工程線: **preflight(入力状態の資格)→ /converge(採用の収束)→ 製造 →
/calibrate(証拠の資格)**。converge を通らない経路(既定設計の実装)も合法。

出自: 前提検査は従来 `/converge` が走るときだけ起きた(トリガー= 設計合成のみ)— 実装・
continuation は前提検査なしで開始され、開始時前提の崩落が反復した(converge 導入日の適用
1 回で開始時前提 5 件が実測で反証= BomDD ECO-032 §0 / 起票前提 3 件の崩落= BomDD ECO-031 /
「既に完了している」という現在状態の未確認= BomDD EXP-20260811-01 第 3 回)。

## 自発起動契約(この節が正本 — Phase 1= entry trigger のみ)

既存状態に依存する作業 — continuation(「●●を実装して」型の再開)・bug fix・既裁定の
適用実装 — を**開始するとき**、人間の呼び出しがなくても本手順を適用する。

> トリガーの機械アンカー可能性(分類のみ — gate 化はしない): 作業開始はタスク受領・起票
> commit として観測可能(hard trigger 候補)。invalidation(作業中の実測・裁定・baseline
> 変更による前提失効)は **Phase 2** — 本版では扱わない(運用実測後に別 ECO)。
> 散文の自発起動は保証されない(`/converge` で実測)— **起動は preflight receipt で
> 観測可能化する**(receipt 不在は**非起動として扱う**。これは運用上の規約であり、実行漏れと記録漏れを区別した判定ではない)。

## 適用範囲(境界宣言)

- **使う**: 既存状態依存タスクの開始時。
- **使わない**: 設計の収束(`/converge` の領分)・証拠の資格査定(`/calibrate` の領分)・
  単純な事実照会。
- **置換しない**: process-core E01(起票が先 — protected 変更の機械 gate)・`/eco-fix` /
  `/eco-accept` の前提確認節・`/bomdd-next`(次作業の選定)。preflight はこれらの**上に載る**
  横断工程であり、各手順内の確認を省く根拠にしない。

## 手順

1. **task classification** — 作業クラスを判定し、**分類と根拠を receipt に必ず記録**する。
   曖昧なら**厳しい側のクラス**を採るか裁定へ上げる(mixed-task 分類誤りは実測済みの故障
   クラス — BomDD ECO-033)。
2. **minimum task contract の読込** — 下の契約表(正本)から該当クラスの必須前提を取る。
3. **repository 固有前提の追加** — 製品側追記領域(表 B)から。
4. **discovered prerequisites** — 本タスク固有に必要と推測した前提は、**最小契約と区別して**
   receipt に載せる(「契約上必要だから missing」と「今回の推測」を混同しない —
   区別を失うと自由推論型へ退化し再現性を失う)。
5. **authoritative source の所在確認** — 各前提の正本(register・order・仕様・裁定台帳・
   git 履歴)を特定する。**AI の記憶・会話文脈だけを正本にしない**(fresh context でも
   同じ判定を再現できること)。
6. **5 状態判定** — 各前提へ 1 状態を付ける:

   | 状態 | 意味 |
   |---|---|
   | confirmed | 存在し、現在状態と一致する |
   | missing | 契約上必要だが存在を確認できない(再構成も不能) |
   | stale | 存在するが基準点より古い・後続変更を反映していない |
   | contradicted | 現在の仕様・実装・裁定と矛盾する |
   | unknown | **確認する手段がない**(missing と混同しない — 測定不能は欠落の証明ではなく、欠落は測定不能ではない) |

7. **開始判定** — **PROCEED** / **PROCEED_WITH_LIMITS**(範囲を縮小して開始 — 縮小内容を
   明記)/ **HOLD**(前提の補完・再構成が先)/ **STOP**。STOP は「**現在の入力状態では作業を
   正当に開始できない**」という**工程判定に限定** — 製品・設計の否定ではない。
   **出口**: HOLD/STOP の override は **reason と decided-by の 2 点必須**で受理し、有効な
   override は receipt へ**件数と宣言者つき**で表示する(出口のないゲートは正当な作業を
   止め、沈黙する免除は fail-open を作る)。
8. **preflight receipt** — 成果物(起票 commit・作業記録)へ埋め込む。新しい artifact 置場は
   作らない。

## task contract 最小表(正本 — 初期 2 クラス)

> **行の追加統制**: 本表への行・クラスの追加は「**欠落事故 1 件の実測**」または「**裁定**」
> 経由のみ — 出典なき増分は過剰 gate への漸進退化であり禁止。追加行には出典を残す。

```text
continuation:
  baseline(開始点の revision・凍結状態):            required
  current-work-state(register/order 等の現在状態):  required
  unresolved-items(未解決・残課題の列挙):           required-or-reconstructable
  handoff-state:                                      required-or-reconstructable
    # artifact 必須ではない — git 履歴・register・order から完全再構成できれば confirmed
  acceptance-target(何が通れば完了か):              required

bug-fix:
  failing-behavior(再現手順・観測):                 required
  target-specimen(対象個体= revision・環境):        required
  expected-behavior(期待の正本):                    required
  acceptance-target:                                  required
```

## 表 B: 本リポ固有の前提(製品リポが所有する追記領域)

> 追記は行の追加統制(上)に従う — 出典つきのみ。

| クラス | 前提 | 出典 |
|---|---|---|
| — | (未記入) | |

## preflight receipt(成果物に埋め込む)

- task classification と根拠
- 前提×判定の表(最小契約 / repo 固有 / discovered を**区別**・各行に正本座標)
- 開始判定と理由(PROCEED_WITH_LIMITS は縮小範囲・HOLD/STOP は不足前提を名指す)
- 有効な override(件数と宣言者 — なければ「なし」と明記)

## 検出力の限界(宣言)

1. **required-known-information absence detector であり、unknown-unknown detector では
   ない** — 契約に無い前提・どこにも記録されていない決定(口頭合意等)は原理的に検出不能。
   言えるのは「契約が要求する前提が確認できない」まで。
2. Phase 1 は entry trigger のみ — **作業中の前提失効(invalidation)は検出しない**(Phase 2)。
3. 判定の再現性は契約の正本化に依存する — discovered prerequisites は推測であり再現保証が
   ない(だから最小契約と区別して表示する)。

## 学習ループ(停止点)

前提の欠落・失効が本手順の**外**で発覚したら(作業中の手戻り・人間の指摘)、次のいずれかへ
分類して記録する: ①**契約行の不足**(→ 実測出典つきで行追加を ECO 提案)②**分類誤り**
(→ receipt の分類根拠を検証)③**Phase 2 領分**(作業中の失効 — invalidation trigger の
必要実測として記録)。契約表の改訂は ECO 経由(検査器が捕捉しないことは許可ではない)。
