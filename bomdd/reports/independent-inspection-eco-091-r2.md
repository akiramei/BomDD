[INFORM / COMPLETE]

REJECT IA-03

- range: 是正確認+回帰
- inspector: EQ-002 / Codex CLI / gpt-5.6-sol
- 対象 revision: 9b496fc7984fa02551183be1a39ee03cda2c2b69
- commit: 0
- 外部 API: 呼出しなし
- 読んだファイル一覧:
  - `bomdd/60-change-order-eco-091.md` §3・§4・§6.1
  - `bomdd/60-change-register.yaml` の ECO-091 エントリ・`allowed_paths`
  - `bomdd/reports/independent-inspection-eco-091.md`
  - `method/tools/self-conformance.py` の C9 関連実装および指定差分

開始時 `git status --short`: 空 / 終了時 `git status --short`: 空

## 判定概要

| 項目 | 判定 | 観測 |
|---|---|---|
| 1. IA-02 の是正確認 | PASS | 属性なしの抽出値は `""`、判定は FAIL、理由は「ResultSummary に outcome 属性がない」。要素不在は `None`、理由は「ResultSummary 不在」で弁別された。`_c9_selftest()` に属性なしの3腕目があり、較正行は「TRX 抽出 3」。 |
| 2. V1/V2 回帰 | PASS | 指定の直接較正は `[]`。V2の4腕は正常対照のみ PASS、予期しない Failed 行・Aborted+Error+exit 2・Failed+Error+exit 1+全行 Passed はすべて FAIL。 |
| 3. r1 境界表の抜き取り | PASS | summary 語彙2行、RunInfo 2行、終了コード×行4行の計8行を再測し、すべてr1と同じ判定。 |
| 4. 窓 | FAIL | `069e0d5..対象 revision` の20パスはすべて ECO-091/092/093 共通 `allowed_paths` 内。一方、`e7d563b..対象 revision` の `self-conformance.py` 差分には IA-02 是正に加えて、C18 witness の検出限界コメント変更が含まれる。「IA-02 の是正に限られること」を満たさない。 |

## 回帰の表

| 入力 | r1 の判定 | r2 の判定 |
|---|---:|---:|
| V2: Completed・exit 0・全行 Passed | PASS | PASS |
| V2: Failed・exit 1・予期しない Failed 行 | FAIL | FAIL |
| V2: Aborted・Error・exit 2・全行 Passed | FAIL | FAIL |
| V2: Failed・Error・exit 1・全行 Passed | FAIL | FAIL |
| summary: Aborted | FAIL | FAIL |
| summary: 未知語彙 `Novel` | FAIL | FAIL |
| RunInfo Error・不合格行なし | FAIL | FAIL |
| RunInfo Error・不合格行あり | PASS可能 | PASS |
| exit 0・不合格行あり | FAIL | FAIL |
| exit 1・不合格行なし | FAIL | FAIL |
| exit 0・不合格行なし | PASS | PASS |
| exit 1・不合格行あり | PASS可能 | PASS |

## 所見

- IA-03 — blocking  
  `git diff e7d563b 9b496fc7984fa02551183be1a39ee03cda2c2b69 -- method/tools/self-conformance.py` は19行変更（16追加・3削除）。IA-02 の抽出・診断文・較正腕・較正行の変更に加え、C18 witness の sparse-checkout に関する検出限界コメントも変更されている。

  C18 の関数本体にコード差分はないが、本ブリーフ項目4は対象ファイルの差分全体が「IA-02 の是正に限られること」を要求している。したがって項目4を FAIL とし、指定基準に従い REJECT と判定する。

## 範囲外の観察

なし。