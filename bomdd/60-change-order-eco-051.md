# Change Order — ECO-051(C17 修理の完全化 — 盲検感度試験の独立所見からの確定・案 A)

> 裁定: user 2026-09-02「A と E を採択して製造まで進めて」— 盲検感度試験 第 1 回
> (bomdd/reports/calibrate-blind-sensitivity-01.md)の起票範囲裁定。本 ECO は A。E は ECO-052。
> 裁定が gate ① を兼ねる。

## 担当設備(equipment)

- 製造: requested/resolved `claude-fable-5-1`・Claude Code(Claude Agent SDK)・来歴 **self-reported**
- 所見の出所: 独立検査官 Codex(要求 gpt-5.6-sol・到達 unknown)検体 S4/S5 — **当方が設計して
  いない変種**。当方 HEAD で 6/6 再現済み(報告 §3.2)。

## 0. 実測(起票根拠)

ECO-049 の use/mention 修理は **backtick fence と見出し語句にしか効いていなかった**。独立検査官が
修理後 revision(S4)で通過を実測した変種: ①チルダ fence 内の見出し ②4 空白インデントのコード例内の
免除宣言(exempt_by 取得)③見出し内の否定「## 較正 receipt は省略した」④空白なし「##較正」
⑤`#` 7 個 ⑥`receiptless`。加えて ⑦対象空集合(`changes: []`)→ PASS 0 件 ⑧fixture 空集合→
「0/0 較正成立」PASS ⑨`verified` 前方一致(`verifiedness` を対象扱い= 予防ゲートの偽陽性)
⑩register 欠落・型異常が未捕捉例外。ECO-049 §4 の「弁別するようになった — 適格」は**当方設計の
対照 7 本だけを測った Q3 型の過大判定**(報告 §4-3)。

## 1. 変更要求(製造対象 — 案 A のみ)

`method/tools/self-conformance.py` の C17 ブロックを次のとおり改訂する:

1. **見出し規則の厳密化**: `#` 2〜6 個+空白必須・`receipt` は語境界(④⑤⑥を排除)。
2. **fence 除去を ``` と ~~~ の両方・未閉鎖は EOF まで**(①)。
3. **免除宣言は行頭でのみ有効**(②)。
4. **receipt 本体の必須項目ラベルを要求**(ECO-051 以降= `C17_BODY_MIN`): 主張と判定 /
   計器欠陥 / 検出力の限界 / battery 行別記録 `asked`(③と旧 P4「見出しのみ」を排除)。
   ECO-041〜050 は見出し規則のみ(歴史的記録は書き換えない — append-only)。
5. **`verified` は厳密一致**(⑨)。
6. **集約 guard**: 対象 0 件 / fixture 0 本 / register 欠落・解析不能・型異常を**構造化 FAIL**
   (⑦⑧⑩ — 型④「測定不能の合格化」の排除)。
7. **独立検査官の変種を fixture F10〜F18 へ恒久化**(known-bad 7 本+known-good 2 本)。
   ラベルの根拠= 修理前 revision で通過・当方 HEAD で再現(査定者から独立)。
8. 限界宣言を改訂((1) を「見出し+本体ラベルの構造的存在」へ・(5)(6) を追加)。

**採らない**: receipt 本体の意味検査(ラベルの存在≠battery 適用の真正 — 限界 (1) 維持)/
病的 receipt(否定見出し+4 ラベル)の弁別(限界 (5))/ 集約 guard の恒久 fixture 化(限界 (6))/
trigger ②③④ の被覆。

## 2. 影響なし予測(反証可能・製造前に凍結)

diff は self-conformance.py の C17 ブロック+台帳系。**既存 verified 10 件(041〜050)は旧 scope
規則で全通過を維持**(scratch 隔離検証で実測済み)。本 order(051)は新 scope 規則の最初の適用個体 —
receipt に 4 ラベルを備えることで通過する見込み。他検査の判定不変。C16 は本 order を required と
判定する見込み。

## 3. 受入

- **V1**: 独立検査官の 6 変種+空集合系 4 件が**遮断へ反転**(10/10)・known-good 4 本が通過・
  旧 scope 10 件が通過(scratch 検証の本体組込み後の再実測)。
- **V2**: fixture 18/18 較正成立・集約 guard 5 腕が FAIL・対照 PASS。
- **V3**: self-conformance 全 PASS(C17 は適用 11 件〔051 含む〕・免除 0)。
- **V4**: CI 緑(headSha 照合)。**V5**: diff 窓。

## /preflight receipt(起動経路: 自発 — 既裁定の適用実装)

- 分類= 既裁定の適用実装(厳しい側= continuation)。状態: baseline `a0366a5`= **confirmed**
  (報告 push 後の HEAD)/ 次番 051= **confirmed**(register 末尾= 050)/ 独立所見の真偽=
  **confirmed**(当方 HEAD で 6/6+空集合系を再現)/ 現行 C17 ブロック実文= **confirmed**
  (実読)/ 既存 10 件の receipt 様式= **confirmed**(見出しレベル・ラベル有無を実測 — ECO-042 の
  事後 receipt は 3 ラベルを持たないため、本体ラベル要求を 051 以降に限定する根拠)。
- 開始判定: **PROCEED**・override 0。

## /converge receipt(起動経路: 自発〔検査器仕様の設計合成〕)

- **判定: 収束**(round 軌跡: 3→0→0)。round 1 = 3 件 — ①行別記録ラベルに `\bNA\b` を含めると
  ECO-045(NA 宣言 ECO)など無関係な文脈に当たる → `asked` のみへ縮小 ②旧 P4 境界(見出しのみ=
  通過)を新 scope で FAIL へ反転することは ECO-049 の宣言を狭める → order §1-4 と限界 (1) で明示
  ③否定見出し+4 ラベルの病的 receipt は通過する → 限界 (5) として宣言(意味は測らない)。
- 検証した主張: 6 変種の通過(HEAD 実測)/ 10 件の receipt 様式(実測)/ 新規則の隔離検証
  (fixture 18/18・10 件通過・集約 guard 5/5・対照 PASS)。
- 未収束事項: なし。

## 4. 製造と受入の実測(2026-09-02)

- diff 監査の窓: baseline `a0366a5`(起票直前 HEAD・起票+製造は同一窓)→ head は受入時に確定。
- C17 ブロックを差し替え(scratch で隔離検証した版を本体へ差し込み・構文 OK)。
- **V1 実測(組込み後)**: 独立検査官の変種 6+空集合系 4 = **10/10 遮断**へ反転 / known-good 4 本
  (見出し+4 ラベル・行頭免除・旧 scope 見出しのみ・verifiedness 非対象)= **通過** / 実 order
  041〜050(旧 scope)= **10/10 通過**・051(新 scope・本 order)= 通過。**V1 PASS**。
- **V2 実測**: fixture **18/18** 較正成立 / 集約 guard= 対象 0 件・fixture 0 本・register 欠落・
  changes 非 list の **4 腕すべて FAIL** / 対照(現行 register)= PASS。**V2 PASS**。
- V3 以降は §5 で確定。

### 較正 receipt(/calibrate 自己適用 — trigger ③: 検査器の変更直後+④: 偽陰性インシデント後。二軸)

- 査定した主張と判定:
  1. 「独立検査官の変種 6 件+空集合系 4 件を遮断する」— **observed / 適格**(10/10 反転・
     fixture F10〜F16 へ恒久化 — ラベルは査定者から独立)。
  2. 「既存の正当な receipt を落とさない(旧 scope 10 件通過)」— **observed / 適格**(10/10・
     known-good 4 本通過が「射程を広げていない」ことの陽性対照)。
  3. 「本修理は当方設計の変種以外にも効く」— **unknown(理由コード: 未実行)** — 第 2 回盲検試験
     (別査定者による再プローブ)まで主張しない。ECO-049 と同じ過大判定を繰り返さない。
- 検出した計器欠陥: なし(本 ECO は独立検査官が検出済みの欠陥の修理)。副次: 差し込み前の scratch
  検証で `NA` ラベルが ECO-045 の無関係文脈に当たることを検出 → `asked` へ縮小(converge round 1)。
- 検出力の限界: 本査定は fixture と受入プローブの範囲。**fixture は独立検査官が既に見つけた変種
  だけ**であり、未知の変種への検出力は測っていない(限界 (1)(5))。
- battery 行別記録:

  | Q | asked/NA | 判定 | 実測 or 読解 | 所見 |
  |---|---|---|---|---|
  | Q1 | asked | observed/適格 | 実測 | 検査文(限界 (1))とコードの一致 |
  | Q2 | asked | observed/適格 | 実測 | known-bad F10〜F16・known-good F17/F18(ラベル独立= 独立検査官) |
  | Q3 | asked | observed/適格 | 実測 | 各変種が独立に落ちる(fixture 個別) |
  | Q4 | asked | observed/適格 | 実測 | fixture ablation で較正不成立へ |
  | Q5 | asked | observed/適格 | 実測 | 対象 0 件・fixture 0 本・register 欠落= FAIL |
  | Q6 | asked | observed/適格 | 実測 | check() 経由で FAILURES へ |
  | Q7 | asked | observed/適格 | 実測 | fixture 0 本= FAIL(沈黙の検出) |
  | Q8 | asked | observed/適格 | 実測 | 行頭の根拠つき免除は通過・件数表示 |
  | Q9 | NA | — | — | 計器個体の刻印は C17 の責務外(self-conformance 全体の env_imprint) |
  | Q10 | asked | observed/適格 | 読解 | 限界 (1)〜(6) |
  | Q11 | asked | observed/適格 | 実測 | fence 2 種・インデント・見出し変種・status 変種をクラス別に |

## 5. CI 実測(V4)

- 対象 revision: `51756e5`(**ローカル HEAD と一致を確認**)
- run 識別子: 33569493872 — 結論: **PASS**(completed/success・headSha 照合済み)
- V3 = self-conformance 全 PASS を**独立観測してから** commit(C17: 適用 10 件・本体ラベル要求=
  051 以降・fixture 18/18・免除 0)。

## 6. クローズ

- diff 監査の窓: baseline `a0366a5` → head `51756e5`(**窓閉鎖**)。窓内は self-conformance.py+
  台帳系のみ — 影響なし予測が的中。
- 受入: V1(10/10 遮断・known-good 4 本・実 order 11 件)/ V2(fixture 18/18・集約 guard 4 腕
  FAIL・対照 PASS)/ V3(全検査緑)/ V4(CI 緑)/ V5(窓)成立。較正 receipt は §4。
- 本 order が **新 scope 規則(4 ラベル+行別 asked)の最初の適用個体** — verified 昇格時の accept 前
  検査で C17 が本 order を新規則で検査する。
- このクローズが支持しないもの: **未知の変種への検出力**(fixture は独立検査官が既に見つけた変種
  だけ — 主張 3 は unknown・第 2 回盲検試験まで主張しない)/ receipt 本体の意味検査 / 病的 receipt
  (否定見出し+4 ラベル)の弁別(限界 (5))/ 集約 guard の恒久 fixture(限界 (6))/ trigger ②③④。
