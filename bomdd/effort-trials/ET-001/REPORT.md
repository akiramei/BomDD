# ET-001 — effort-calibration の初回実使用(EXP-20260903-03)

> 測定器: [`method/tools/effort-calibration.py`](../../../method/tools/effort-calibration.py)(ECO-058・verified)。
> 本 trial は測定器の**初回実使用**であり、Effort の過不足に関する主張はしない(下記「支持しないもの」)。
> 正本= [`trial.yaml`](trial.yaml)・[`runs/`](runs/)(execution / evaluation receipt・追記のみ)。
> 導出物= [`projection.yaml`](projection.yaml)(`project` の出力・再生成可能・正本ではない)。

## 1. 課題と treatment

- **課題**(`input/TASK.md`・sha256 = trial.input_hash): C16 ゲートの判定規則を**散文仕様**として与え、
  12 検体の PASS/FAIL を予測させる。検体は本セッションで実測した失敗型②(検索打ち切り)・③(意図と
  実文の混同)・⑧(use/mention)と同族の「規則の相互作用」(フェンス内 hard-positive・未閉鎖 fence・
  見出し境界・conflict の優先・遺産/新規則の閾値)を 1 検体 1 論点で置いた。
- **oracle**: 実装そのもの(`converge_verdict` @ `00a3190`)で期待表を計算し、run 開始前に
  `rubric/rubric.md` へ封印(sha256 = trial.rubric_hash)。散文仕様への転写忠実性は oracle では測らない
  (TASK.md 内の検体本文が `samples/*.md` と byte 一致することは実測済み・12/12)。
- **評価者**: `rubric/evaluate.py`(oracle スクリプト)。treatment を受け取る引数を持たない —
  盲検は**構造**で担保(測定器の限界 (3) のとおり、行動上の盲検はこれ以上測れない)。
- **treatment**(4 種 × 反復 2 = 8 run・全て並列・同時刻開始):

  | tag | requested effort | method_stack | 備考 |
  |---|---|---|---|
  | M | medium | なし | codex exec `-c model_reasoning_effort=medium` |
  | H | high | なし | 同 high |
  | MC | medium | converge.md(正本 sha256 を receipt に記録) | 課題文の前に付加(`input/converge-addendum.md`) |
  | HC | high | 同上 | |

  model requested = `gpt-5.6-sol`(`~/.codex/config.toml` 既定)/ **resolved = unknown**(到達確認の
  経路なし — 推定で埋めない)。harness = Codex CLI 0.144.1・sandbox read-only・prompt は stdin。

## 2. 結果(evaluation receipt → projection)

| treatment | n | pass | pass_rate | mean tokens(in+out) | reasoning tokens(run 別) |
|---|---|---|---|---|---|
| M | 2 | 2 | 1.0 | 19,055 | 469 / 483 |
| H | 2 | 2 | 1.0 | 19,032 | 457 / 461 |
| MC | 2 | 2 | 1.0 | 34,888 | 886 / 1,461 |
| HC | 2 | 2 | 1.0 | 51,692 | 2,680 / 2,586 |

- **effort 感度(導出)**: M↔H = `unsupported`(1.0 vs 1.0)/ MC↔HC = `unsupported`(1.0 vs 1.0)。
- 8 run すべて 12/12 正答・observed_failures 空。**天井効果** — 課題が全 treatment で解けており、
  本 trial は Effort の差を**弁別できない**(unsupported は「差がない」の証明ではない)。
- reasoning tokens は非 C 腕で M と H に差がない(457〜483)。到達 effort は unknown のため
  「high が適用されなかった」と「課題が容易で推論量が飽和した」を**弁別できない**(+C 腕では
  M→H で reasoning が増えており、後者の可能性を支持するが確定しない)。
- converge 付加は正答率を変えず、コストを 1.8×(M)〜2.7×(H)にした。収束 receipt の添付は 4/4 run で
  観測(最終メッセージ末尾)。

## 3. 製造中の自己捕捉(実行器の欠陥・評価前)

- `codex exec -o RESULT.md` の相対パスは `-C` ではなく**本プロセスの cwd 基準**で解決され、8 run が
  同一ファイルを上書き → 全 run の RESULT.md が空・output_hash が空文字列のハッシュで receipt に書かれた。
- **是正**: 最終メッセージは `--json` の events(item.completed/agent_message)にも残るため、そこから
  復元して output_hash を再計算(`run-trial.py recover-outputs` — evaluation receipt が 1 件でもあれば拒否
  する。復元は**評価前・コミット前**に実施。各 receipt に `output_recovered_from` を残した)。以後の
  実行器は絶対パスで `-o` を渡し、events からの抽出を照合に使う。
- 初回の起動は Windows で `codex` が `codex.cmd` に解決されず 8 run 全滅(receipt 0 件・記録なし)。
  `shutil.which` で解決するよう是正して再実行。
- codex 起動時に「failed to install system skills」(並列起動の競合)が 5/8 run の stderr に出た。
  exit code は 0・応答は完了しており、本課題は system skills を使わないが、**環境ノイズとして記録**する。

- 記録は sha256 で座標結合されている(trial → execution → evaluation)ため、`bomdd/effort-trials/.gitattributes` で
  `-text`(改行変換なし・byte 保存)を宣言した。実行器は Windows の text モードで CRLF を書いており、変換されると hash 整合が壊れる
  (根本は書き込み側の newline 明示 — playbook §13 の I/O 規律・次の実行器で是正)。

## 4. EXP-20260903-03 の 3 問への回答

1. **trial 定義の凍結と receipt の手動記帳**: 起きた。input/rubric の hash を trial.yaml へ封印し、
   `execute` が実行前に照合(改変なら停止)。execution receipt 8 件・evaluation receipt 8 件が別コマンド・
   別イベントで残った。アンカー未結線のため散文契約(本セッションの手順)による — 非起動が起きても
   本測定器は検出できない(限界 (1))。
2. **評価者が実行者と別で盲検か**: 別(oracle スクリプト)・構造的盲検(treatment を渡す経路なし)。
   人間/AI 評価者の盲検はこの trial では測っていない。
3. **project の出力と policy 非連動**: `unsupported` ×2 を出し、それを「High を使う/使わない」判断に
   **使っていない**(本 report は判断を書かない — 記録の蓄積のみ)。

## 5. このクローズが支持しないもの

- Effort の過不足そのもの(天井効果・弁別力なし)。**次の trial は known-fail を含む課題**(基準線で
  少なくとも 1 treatment が落ちる)でなければ感度は測れない。
- 到達 effort・到達モデル(unknown)。
- 散文仕様の転写忠実性(oracle は実装・仕様は転写 — 12 検体で不一致は出なかったが、それは
  「転写が正しい」の証明ではなく「8 run が一致した」の観測)。
