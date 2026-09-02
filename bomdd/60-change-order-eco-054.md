# Change Order — ECO-054(空集合 fail-open の横断是正〔型④〕— C9 `total: 0` / ui-cad 空成果物・案 B)

> 裁定: user 2026-09-02「P3 別 ECO として起票」(calibrate 改善案の converge・延長 1 周で収束)。
> **本裁定は起票の承認であり、製造着手は別途の裁定を待つ**(status: filed)。P4(C9 個別)・
> P5(ui-cad 個別)は見送り・個別実測待ち。

## 担当設備(equipment)

- 起票: requested/resolved `claude-fable-5-1`・Claude Code(Claude Agent SDK)・来歴 **self-reported**
- 所見の出所: 盲検感度試験 第 1 回の独立検査官(Codex・検体 S1/S3= C9・S2/S6= ui-cad)—
  **当方が設計していない所見**。C17 の同型は ECO-051 で是正済み。

## 0. 実測(起票根拠)

- **型④(測定不能の合格化)が 3 計器に横断**して存在した(bomdd/reports/calibrate-blind-sensitivity-01.md
  §3.2・§4-4)。C17 は ECO-051 の集約 guard で FAIL 化済み。残る 2 計器:
  - **C9**: suite の `total: 0`+空 TRX が「0/0 合格」で PASS(独立検査官 2 名が独立に再現・当方は
    機構を読解で整合確認: manifest 読込が `yaml.safe_load`・`o != "Passed"` を一律失敗扱い・
    `returncode` は trx 欠落時のみ参照)。
  - **ui-cad-gate**: 必須成果物すべて `{}`・raw なし・`--mock` なし → GU2〜GU5 が空母集団で PASS・
    GU1/GU6 は built-in NA → **exit 0・「昇格可(実行 4/6・NA 1 件)」**(当方 HEAD で実測)。
- 実害: 現行 manifest の 4 suite は total>0・BomDD 内の ui-cad consumer は C6 fixture のみ — **実害は
  未実測**。起票根拠は実害でなく**系統性**(同一故障型が独立 3 計器に存在し、本リポが ECO-002/008
  以来もっとも重く扱う類型)。

## 1. 変更要求(製造対象 — 案 B のみ)

1. **C9**: suite の `total == 0` または結果集合が空のとき **FAIL**(「空結果は合格ではない — 測定不能は
   合格ではない」)。`expected_failed` の受理・signature 突合は不変。
2. **ui-cad-gate(二層)**: (a) 必須成果物の**欠落・スキーマ不成立**(top-level が mapping でない・
   必須キー欠落)→ **exit 2(入力不正)**(現行の未捕捉例外を構造化)。(b) 成果物は存在するが
   **母集団 0** のゲート(GU2〜GU5 の検査対象が空)→ **昇格判定保留(exit 1)**・理由「母集団 0」。
   §15 経過措置の built-in NA(GU1+GU6・raw なし)とは**弁別を維持**(NA は宣言された不適用・
   母集団 0 は測定不能)。
3. **fixture(known-bad / known-good)**: C9= `total: 0`+空 TRX 腕(FAIL)・正常 suite 腕(PASS)/
   ui-cad= 全 `{}` 腕(exit 2)・母集団 0 腕(保留 exit 1)・正常組 6/6 腕(exit 0)。ラベルの根拠=
   独立検査官の実測(S1/S3/S2/S6)— 査定者から独立。
4. 両計器の限界宣言を改訂(型④の排除範囲・NA と母集団 0 の弁別・意味検査は非対象)。

**採らない**: P4(C9 の `NotExecuted`・runner exit・`safe_load` → strict)/ P5(ui-cad の GU2 open-question・
識別子欠落・型不正の網羅・rejected 表示・常設対照)— いずれも個別実測待ち(裁定)。

## 2. 影響なし予測(反証可能・製造前に凍結)

- C9: 現行 manifest は全 suite total>0 → **判定不変**の見込み。
- ui-cad: BomDD 内の consumer は C6 fixture のみ。**リスク**: C6 fixture は `36-ui-dictionary.yaml` に
  `actions: {}` を持つ(ECO-045 で追加)— 母集団 0 判定が GU4 に当たると C6 が赤化しうる。製造時に
  実測し、当たる場合は「辞書の空 actions は GU4 の母集団ではない」等の弁別を仕様で明示する
  (fixture の書き換えでなく規則の精密化で解く — 判定を書き換えて通さない)。
- 製品リポ側の実運用への影響は**未測定**(境界: ui-cad は配布治具)。

## 3. 受入(製造着手後)

- **V1**: C9 `total: 0` 腕が FAIL・正常腕 PASS / ui-cad 全 `{}` が exit 2・母集団 0 が exit 1・正常組 exit 0・
  built-in NA(raw なし+mock なし・母集団あり)は現行どおり昇格可。
- **V2**: fixture 全成立・C6 判定不変(または弁別規則の明示)。
- **V3**: self-conformance 全 PASS。**V4**: CI 緑。**V5**: diff 窓。

## /preflight receipt(起動経路: 自発 — 既裁定の適用実装〔起票〕)

- 分類= 既裁定の適用実装(厳しい側= continuation)。状態: baseline `771d80b`(起票時)→ 製造着手時に **`c00de99` へ再確認**(起票 commit が間に入ったため)/ 次番 054=
  **confirmed**/ C9・ui-cad の残存= **confirmed**(本日 HEAD 実測・ECO-051/053 は両計器に無変更)/
  C6 fixture の `actions: {}`= **confirmed**(ECO-045 記録)/ 製造着手の可否= **unknown(理由コード:
  裁定待ち)** → status: filed。
- 開始判定: **PROCEED(起票のみ)**・override 0。

## /converge receipt(起動経路: 自発 — 本 ECO の設計〔改善案集合の converge とは別〕)

- **判定: 収束**(round 軌跡: 2→0→0)。round 1 = 2 件 — ①ui-cad の空集合は「欠落/スキーマ不成立」と
  「母集団 0」で帰結が違う(入力不正 exit 2 / 保留 exit 1)→ 二層化 ②C6 fixture の `actions: {}` が
  母集団 0 に当たりうる → 影響なし予測にリスクとして凍結(判定の書き換えで通さない)。
- 起動経路: 自発。DoD: アンカー ✔(C9= self-conformance 実行 / ui-cad= gate 実行)/ 実装先 ✔(C9 manifest
  読込・結果集合比較 / ui-cad collection 取得と最終判定)/ 赤 fixture ✔(§1-3)/ 所有者 ✔(fixture が
  検査ごと)/ 複雑性 ✔(規則の精密化のみ・新設備なし)。
- 検証した主張: C9 機構(本日 HEAD 読解)/ ui-cad 全 `{}` exit 0(本日 HEAD 実測)/ C6 fixture の内容
  (ECO-045 §)/ ECO-051 の C17 集約 guard(実装済み)。
- 未収束事項: なし。

## 4. 製造と受入の実測(2026-09-02・user「ECO-054 の製造まで進めて」)

- diff 監査の窓: baseline `c00de99`(製造着手時の HEAD — 起票 commit の後)→ head は受入時に確定。
- **製造前の実測(C6 fixture)**: ui-ir に action 1 件・bom/trace は空・action は根拠つき rejected で被覆
  (C6b は exit 0 を期待)。**ゲートごとの母集団 0 判定だと C6b が赤化**する(§2 で凍結したリスクの
  実発生)→ 規則の精密化: **母集団 0 は根(ui-ir の actions+raw の interactables)で判定**し、根が非空
  なら下流の空は既存ゲート(GU2 の未会計検出)の所見として現れる。C6 の意図は保存(fixture は不変)。
- **製造**: C9= suite 判定を純関数 `_c9_suite_verdict` へ抽出(挙動保存)し空結果 guard(結果 0 件または
  total 0 → FAIL)を追加・`_c9_selftest` に腕 3 本(known-bad 2・known-good 1)を追加(5→8 腕)。
  ui-cad= 二層(スキーマ不成立→ exit 2 / 根の母集団 0 → 保留 exit 1・`--na "population: 理由"` で
  契約上の NA 宣言可)・`--selftest`(3 腕)・限界宣言。
- **V1 実測**: C9 selftest 8/8 成立(total 0+空= FAIL / total 2+結果 0= FAIL / 2/2 合格= PASS)/ ui-cad:
  全 `{}`= **exit 2**(「ui-ir に actions がない」)/ 母集団 0(スキーマ成立)= **exit 1**(保留・母集団 0)/
  C6b 型(根 1・根拠つき rejected)= **exit 0** / C6a 型(理由なし rejected)= exit 1 / rulings が list=
  exit 2 / 母集団 0+`--na population`= exit 0(NA 2 件表示)/ `--selftest`= PASS 3 腕。**V1 PASS**。
- **V2 実測**: 両計器の fixture 全成立・C6 の判定は不変(C6a 遮断・C6b 通過 — 規則の精密化で解決・
  fixture 不変)。**V2 PASS**。
- **製造中の判断**: §1-2(b)「GU2〜GU5 の検査対象が空 → 保留」を、C6 実測に基づき「**根の母集団 0**
  → 保留」へ精密化(下流の空はゲート所見として既に現れる)。§1 の文言より狭い実装であり、限界
  宣言に「母集団 0 の判定は根のみ」を明記。
- V3 以降は §5 で確定。

### 較正 receipt(/calibrate 自己適用 — trigger ③: 検査器の変更直後+④: 独立所見の是正。二軸)

- 査定した主張と判定:
  1. 「空集合の合格化を C9/ui-cad で排除した」— **observed / 適格**(known-bad 腕が FAIL・selftest へ
     恒久化 — ラベルは独立検査官 S1/S3/S2/S6 の実測で査定者から独立)。
  2. 「既存の正当な判定を壊さない」— **observed / 適格**(C6a/C6b 不変・C9 正常腕 PASS・built-in NA
     維持・`--na population` の出口あり)。
  3. 「製品リポの実運用でも同じ帰結になる」— **unknown(理由コード: 未実行)** — BomDD 内 consumer は
     C6 のみ・ui-cad は配布治具。
- 検出した計器欠陥: なし(本 ECO は独立検査官が検出済みの欠陥の修理)。副次: §1-2(b) の文言が
  C6 fixture を赤化させる過広さを製造前に検出し規則を精密化。
- 検出力の限界: 母集団 0 の判定は根のみ(各ゲート固有の空集合は測らない)/ C9 の `NotExecuted`・
  runner exit・`safe_load`(P4)と ui-cad の GU2/識別子/rejected 表示(P5)は対象外。
- battery 行別記録:

  | Q | asked/NA | 判定 | 実測 or 読解 | 所見 |
  |---|---|---|---|---|
  | Q1 | asked | observed/適格 | 読解 | 限界宣言(根のみ・P4/P5 対象外)とコードの一致 |
  | Q2 | asked | observed/適格 | 実測 | known-bad/known-good 対(ラベル= 独立検査官) |
  | Q3 | asked | observed/適格 | 実測 | 腕ごとに独立に落ちる(C9 3 腕・ui-cad 3 腕) |
  | Q4 | asked | observed/適格 | 実測 | selftest は本体関数/本体プロセスを実入力で実行 |
  | Q5 | asked | observed/適格 | 実測 | 空結果・母集団 0 を PASS に数えない(本 ECO の主題) |
  | Q6 | asked | observed/適格 | 実測 | check()/exit code 経由 |
  | Q7 | asked | observed/適格 | 実測 | selftest が常設陽性対照(ui-cad は本 ECO で初設置) |
  | Q8 | asked | observed/適格 | 実測 | `--na population` の根拠つき出口・件数表示 |
  | Q9 | NA | — | — | 個体刻印は ui-cad の宣言済み境界(revision 非刻印) |
  | Q10 | asked | observed/適格 | 読解 | 限界: 根のみ・P4/P5・製品リポ影響 unknown |
  | Q11 | asked | observed/適格 | 実測 | スキーマ不成立/母集団 0/根拠つき rejected/理由なし をクラス別に |

## 5. CI 実測(V4)

- (push 後に記入)

## 6. クローズ

- (受入時に記入)
