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

- 分類= 既裁定の適用実装(厳しい側= continuation)。状態: baseline `771d80b`= **confirmed**/ 次番 054=
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

## 4. 製造と受入の実測

- (製造着手の裁定後に記入)

## 5. CI 実測(V4)

- (push 後に記入)

## 6. クローズ

- (受入時に記入)
