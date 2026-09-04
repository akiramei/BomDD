# Change Order — ECO-060(型④の横断是正 第 2 弾 — ET-002 掃引で判明した C3 / C10 / C11b / C16 と同型 C11 / C4 の空母集団ガード)

> 裁定: user 2026-09-04「型④ 4 計器の是正 ECO を起票して製造まで進めて」。裁定が gate 1 を兼ねる。
> 対象列挙の根拠= ET-002(型④横断掃引・4 腕 × 2 反復・腕の指摘を実文で裁定)。**§8.2 追補④(クローズ節に同型掃討の
> 対象列挙)と §13 第 5 様態(同族計器の横断掃引をクローズ条件へ)の初適用。**

## 担当設備(equipment)

- 製造: requested/resolved `claude-fable-5-1`・Claude Code(Claude Agent SDK)・来歴 **self-reported**
- 対象列挙の出所: ET-002 の 8 run(Luna none/medium/high・Sol medium)+製造者の裁定(実文)— 是正者以外の出所を含む(OBS-20260902-03)

## 0. 実測(起票根拠)

- ECO-054 は型④(空母集団の無音 PASS)を C17 / C9 / ui-cad の 3 計器で是正し、「第 4 の計器の有無は横断掃引未実施」と
  範囲を明示して閉じた。ET-002([REPORT](effort-trials/ET-002/REPORT.md) §5)が全 21 ゲートを掃引し、構造として型④を持つ
  ゲートが **C3・C10・C11b・C16** の 4 本、加えて採点除外の **C8**(8/8 腕 SILENT)・**C4**(4/4 で割れ)を実測。
- C3 は verified 0 件の台帳で PASS「(全 verified 適合)」を返すことを関数実行で確認(ET-002 rubric 封印時)。

## 1. 変更要求(製造対象)— 同型掃討の対象列挙(21 ゲート悉皆)

| ゲート | 処置 | 内容 |
|---|---|---|
| C3 | **是正** | `_c3_problems(reg)` へ抽出。verified 0 件は問題(FAIL)。PASS 行に verified 件数 |
| C10 | **是正** | `_c10_structural_drifts`: テンプレの宣言対象キー(ui-ir / trace-map)が 0 件なら乖離(FAIL) |
| C11b | **是正** | `_c11_controls(r)`: IQ/OQ control 0 件は `det` 不成立(FAIL)。PASS 行に control 件数 |
| C16 | **是正** | `_c16_population_problems`: order と improvements 節を母集団別に非空要求。PASS 行に 2 母集団の件数 |
| C11 | **是正(同型)** | run 1 の control 0 件は `det_ok` 不成立。PASS 行に control 件数(C11b と同じ走査形) |
| C4 | **是正(同型)** | 生成 YAML 0 件は `gen_bad`(FAIL)。腕は 4/4 で割れたが実文では非空ガードなし |
| C8 | **良性確定** | リポ直下 entry の不在検査。構造的に空にならない集合(検査スクリプト自身がその直下にある)— 変更なし |
| C1 C2 C13 C15 C17 C9 | 対象外 | 既存ガードあり(ET-002 oracle・腕とも OK) |
| C7 C12 | 対象外 | PASS 行に件数/空リスト表示あり(定義 (b))。Luna none 腕のみ SILENT と判定— 定義の未適用 |
| C5a C5b C6a C6b C14 C18 | 対象外 | 固定操作(走査母集団なし) |

**陽性対照**: `_type4_selftest()`(C3 の冒頭で毎回実行・常設)— 空母集団で `_c3_problems` / `_c11_controls` /
`_c16_population_problems` / `_c10_structural_drifts`(空テンプレ)が FAIL 側へ倒れることを確認してから走査する。
不成立なら C3 を FAIL(計器を先に疑う)。C4 / C11 のガードは陽性対照を持たない(scaffold 実行を要するため — 限界として宣言)。

**採らない**: C8 の変更 / 上流 runner(process-qualification.py)の control 母集団の検査(C11 の腕の主張は runner 側の
話 — 別途)/ ui-cad-gate・effort-calibration など self-conformance 外の計器(ECO-054 で是正済み)。

## 2. 影響なし予測(反証可能・製造前に凍結)

本リポの現状で全母集団は非空(verified 多数・テンプレキー 8/7・control 群あり・order 41+節あり・生成 YAML あり)のため、
全検査の判定は不変で PASS 行の件数表示だけが変わる。diff は self-conformance.py 1 本+台帳系。

## 3. 受入

- **V1**: `_type4_selftest()` が現行コードで空(4 関数が空母集団で FAIL 側)— かつ**ガードを外した変異**で非空になる(較正)。
- **V2**: self-conformance 全 PASS(判定不変・件数表示の追加のみ)。**V3**: CI 緑。**V4**: diff 窓。

## /preflight receipt(起動経路: 自発 — 既裁定の適用実装)

- baseline `aa43d89`= **confirmed**(HEAD・origin/main 一致・作業木 clean)/ 次番 060= **confirmed**(register 末尾= 059)/
  対象列挙= **confirmed**(ET-002 REPORT §5)。開始判定: **PROCEED**・override 0。

## 4. 製造と受入の実測(2026-09-04)

- 記入は受入時。

## 5. CI 実測(V3)

- 記入は受入時。

## 6. クローズ

- 記入は受入時。
