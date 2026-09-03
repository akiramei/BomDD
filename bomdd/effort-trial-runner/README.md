# effort trial 実行器(ET-002 以降)

[`run-trial.py`](run-trial.py) は測定器 [`effort-calibration.py`](../../method/tools/effort-calibration.py)(ECO-058)の
**記録を作る側**で、判定はしない。ET-001 の [`rubric/run-trial.py`](../effort-trials/ET-001/rubric/run-trial.py) を
一般化し、実測した欠陥(`-o` の cwd 基準解決・`codex.cmd`・CRLF 書き込み)を是正したもの。
`bomdd/effort-trials/` 直下に置かないのは、validate がそこを trial として走査するため。

## ET-002 の準備状態(2026-09-04)

- plan: [`plan-ET-002.yaml`](plan-ET-002.yaml) — Luna none / medium / high + Sol medium(EXP-20260903-04)。
- 各腕の到達確認: `probe --plan plan-ET-002.yaml`(1 行プロンプト × 4 腕・到達モデルは確認できない)。
  **2026-09-03 15:05Z(JST 09-04 00:05)の probe は 4 腕とも UNKNOWN**(codex backend が HTTP 404 — 1.5 時間前に成功した同一の
  手動呼び出しも同時刻に 404。サービス側の事象で実行器の欠陥ではない。ET-002 開始前に再 probe する)。
  2026-09-03 の手動 probe では `-m gpt-5.6-luna` の effort none / high が応答済み。
  **再 probe(2026-09-04・user 指示)= 4 腕とも exit 0・応答 `OK`**(LN/LM/LH: input 15,504・SM: input 14,667・reasoning 0 —
  1 行プロンプトのため推論量の差は出ない。到達モデルは今回も events に刻印なし= unknown)。ET-002 の到達確認は完了。
- 陽性対照: `python run-trial.py --selftest`(codex を呼ばず init → 合成 execution → evaluate → validate)。

## ET-002 を始める条件(EXP-20260903-04)

1. **実タスク**で Effort の過不足が疑われたこと(測るために課題を作らない・難しくしない)。
2. oracle または機械比較できる出力があること。評価スクリプトは trial ごとに書く(引数は出力ファイル 1 つ —
   treatment を渡す経路を持たせない)。
3. ~~effort 序数に `none`(と `max`)を追加する ECO~~ → **ECO-059 で追加済み(2026-09-04・none〜max の 6 段)**。
   Luna none を含む対も投影で序数どおりに分類される。

## 手順

```bash
python bomdd/effort-trial-runner/run-trial.py init bomdd/effort-trials/ET-002 --input input/TASK.md --rubric rubric/rubric.md --vocab <症状語彙 CSV> --repetitions 2
```

```bash
python bomdd/effort-trial-runner/run-trial.py dry-run bomdd/effort-trials/ET-002 --plan bomdd/effort-trial-runner/plan-ET-002.yaml
```

```bash
python bomdd/effort-trial-runner/run-trial.py execute bomdd/effort-trials/ET-002 --plan bomdd/effort-trial-runner/plan-ET-002.yaml --scratch <scratch dir>
```

```bash
python bomdd/effort-trial-runner/run-trial.py evaluate bomdd/effort-trials/ET-002 --evaluator bomdd/effort-trials/ET-002/rubric/evaluate.py
```

```bash
python method/tools/effort-calibration.py project bomdd/effort-trials
```

rubric と評価スクリプトは **execute の前に**確定する(init が hash を封印し、execute が照合する)。
