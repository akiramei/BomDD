# Change Order — ECO-068(計器の selftest が前提不在(OS temp・git)で Traceback を出す — bomdd-run / bomdd-witness / bomdd-job の selftest を `UNMEASURABLE <CAUSE>` の 1 行報告へ〔起票のみ〕)

> 裁定: user 2026-09-11 DECIDE「A」(還元と小是正を先に)— Phase 6 実 cell 実測(ECO-062 §10.7 P6-01)の帰結。出典= [phase6-realcell-eco-067.md](reports/phase6-realcell-eco-067.md) §4、
> improvements.md 2026-09-11 還元節(OBS-20260727-10 の 3 例目・織り込み案 C)。**起票のみ**(製造着手は別裁定)。起票工程は job 経由。

## 担当設備(equipment)

- 起票: requested/resolved `claude-fable-5-1`・Claude Code(Claude Agent SDK)・来歴 **self-reported**

## 0. 実測(起票根拠)

### 0.1 実測(2026-09-11・Phase 6 実 cell・Codex read-only sandbox)

- cell 内で `python method/tools/bomdd-run.py --selftest` → **exit 1・1 行目 `Traceback (most recent call last):`**(OS temp が使えず `tempfile.TemporaryDirectory()` が
  FileNotFoundError・`selftest()` の with 文の外側に例外処理がない)。同じ環境で `bomdd-witness.py verify` は `UNMEASURABLE TREE_UNAVAILABLE(TEMP_UNAVAILABLE): …` を 1 行で返した
  (本体は ECO-066 で原因分離済み・selftest は未対応)。
- 同型(実読): `bomdd-witness.py selftest()`(:`with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as wd:` を try で包んでいない)・`bomdd-job.py selftest()`(同)・
  `bomdd-run.py selftest()`(同)。self-conformance.py は範囲外(C11/C14 の temp は `_cleanup_tmp` 側・ECO-065 で扱い済み・selftest 相当の経路は別途)。
- 帰結: 「測定不能は合格ではない」の裏側= **測定不能を測定不能として報告できない**(traceback は無報告と同じ・§13「計器は自分の前提を自分で満たす」の selftest 側の欠け)。
  運転員・製造セルが selftest を回す Phase 6 以降は、traceback が 1 行目に来ると入口の判定行の契約(W6/R7 と同型)も崩れる。

### 0.2 起票工程(job 経由)

`bomdd-job.py ECO-068` を register 追記後に出力し required_skills / skills_missing を /preflight receipt に記す。

## 1. 変更要求(製造対象の候補 — 製造裁定時に凍結・対象= 3 ツールの `selftest()` のみ)

1. **selftest の前提不在を 1 行で報告**: `selftest()` の一時ディレクトリ生成と git 初期化を try で包み、失敗は `UNMEASURABLE TREE_UNAVAILABLE(<CAUSE>): selftest の前提不在 — <detail>`
   (CAUSE= TEMP_UNAVAILABLE / GIT_UNAVAILABLE)を 1 行印字して **exit 2**(selftest 失敗の exit 1 と区別・測定不能は合格ではない)。traceback を出さない。
2. **対象 3 ツール**: `bomdd-witness.py`・`bomdd-run.py`・`bomdd-job.py`。共通 helper は置かない(3 ファイルに各 10 行程度・依存を増やさない)。
3. **陽性対照**: 各 selftest に「temp 不能」腕を持たせるのは自己言及になる(selftest が temp を使う)ため、**受入側の外部プローブ**で測る(§3 V1: `tempfile.tempdir` を不在パスにした
   子プロセスで `--selftest` を回し、1 行目と exit 2 を確認)。

**採らない**: self-conformance.py の selftest 系(範囲外・別 OBS)/ 共通 helper の新設 / selftest の内容(腕)の変更 / 本体(verify・run)の変更(ECO-066/067 で済み)。

## 2. 影響なし予測(起票段階・反証可能)

起票の diff は台帳系のみ。製造時(候補): 3 ファイルの `selftest()` 冒頭のみ(各 +10 行程度)。本体経路・1 行目の契約・終了コードの意味(0/1/2)不変。selftest の腕は不変。
C1〜C18 判定不変(3 ツールは検査対象集合外)。kit 非含有・製品リポ非波及。

## 3. 受入(製造時の候補)

- **V1**(外部プローブ): 3 ツールそれぞれに `tempfile.tempdir=<不在パス>` の子プロセスで `--selftest` → 1 行目 `UNMEASURABLE TREE_UNAVAILABLE(TEMP_UNAVAILABLE): …`・exit 2・traceback なし。
  `PATH=""` で `GIT_UNAVAILABLE`。通常環境では従来どおり `ADVANCE OK: selftest PASS…` exit 0。
- **V2**(実環境): Phase 6 実 cell(Codex read-only)で `bomdd-run.py --selftest` を再実行 → 1 行 UNMEASURABLE・exit 2(織り込み案 C の効果測定)。
- **V3**: self-conformance 全 PASS・CI 緑・窓= 3 ファイル+台帳系。**V4**: 独立検査= **製造者較正のみで受入を当方案**(3 ファイル各 10 行の局所変更・本体経路非接触・
  ECO-065 A 案と同じ整理。異系統検査を要するなら製造裁定で指定)。

## /preflight receipt(起動経路: **job 経由** — `bomdd-job.py ECO-068` の出力を開始 artifact として読んだ)

- 分類= 既裁定の適用実装(user DECIDE「A」・起票まで)。baseline `77b966c`= **confirmed**(HEAD・作業木 clean)/ 次番 068= **confirmed**(register 末尾= 067)/ 実測= **confirmed**
  (phase6-realcell-eco-067.md §4 の cell 報告・3 ツールの selftest 冒頭を実読)/ 凍結の非該当= **confirmed** / 同一ファイルへの進行中 ECO なし= **confirmed**(ECO-066/067 は verified)。
- job ビュー: required_skills= `["calibrate", "preflight"]`・skills_missing(起票時)= `["calibrate"]`(order 生成前の初回出力は null= order 不在の unknown・生成後に再出力して訂正。calibrate は verified 昇格時の較正 receipt で応答)
- 開始判定: **PROCEED**(起票まで)・override 0。製造は別裁定。

## /converge receipt(起動経路: 自発 — 是正案の設計〔helper か各ファイルか・exit の値〕)

- **判定: 収束**(round 軌跡: 2→0→0)。
- DoD: ✔ 前提不在が 1 行の UNMEASURABLE で出る / ✔ selftest 失敗(exit 1)と測定不能(exit 2)を区別 / ✔ 本体経路・腕・契約は不変 / ✔ 陽性対照は自己言及を避けて外部プローブ。
- round 1(新規 2 件): ①共通 helper を tools 直下に置くと import 依存(job→witness→run)が増える → 各ファイル 10 行 ②selftest 内に temp 不能腕を置くと selftest 自身が temp を要する →
  外部プローブで受入。round 2/3: 新規 0。**未収束事項: なし**。

## 記録(起票時)

- register: `filed`(2026-09-11)・baseline `77b966c`・allowed_paths(起票段階)= 3 ファイル+台帳系(製造裁定で再凍結)。
- **次の裁定(製造裁定)**: 範囲= §1 の 3 項をそのまま / 独立検査= 製造者較正のみ(当方案)か Codex か。
