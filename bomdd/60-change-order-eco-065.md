# Change Order — ECO-065(self-conformance の temp 後片付けが無音で失敗する — `rmtree(ignore_errors=True)` 8 箇所の fail-silent を是正〔起票のみ〕)

> 裁定: user 2026-09-11「C14 の temp 残置を直す ECO を起票して」— ECO-064 §8.1 付随発見・OBS-20260911-02 の帰結。**起票のみ**(製造着手は別裁定)。
> 起票工程は **job 経由**(§0.4)— Phase 4 の 3 本目候補(required_skills が非 null の状態で回す初の ECO)。

## 担当設備(equipment)

- 起票: requested/resolved `claude-fable-5-1`・Claude Code(Claude Agent SDK)・来歴 **self-reported**

## 0. 実測(起票根拠)

### 0.1 残置の実測(2026-09-11・`%TEMP%`)

| prefix | 件数 | 総量 | 中身 | 出所 |
|---|---|---|---|---|
| `bomdd-selfconf-c11-*` | **350** | **1,154 MB** | `AdaptSmoke/.git/objects`・`ProcCoreSmoke/.git/objects`(read-only `-r--r--r--` の loose object) | C11 process-core 適格性(scaffold+git init+commit) |
| `bomdd-selfconf-c14-*` | 11(当方が 277 件削除後・sandbox 所有 4+新規 7) | 5 MB | `origin/.git/objects` | C14 kit-freshness 対照実測 |

- 発生率: self-conformance 1 回あたり c11 1 件+c14 2 件が残る(直近 1 回の前後で観測)。ECO-064 の弧だけで 6 回実行= 18 件。
- 2026-08-02 以降の累積(c11 の最古= 2026-08-02)。当方は 2026-09-11 に c14 277 件を削除(§8.1 ECO-064)— **c11 の 350 件は本起票時点で未削除**(製造裁定と同時に判断)。
- 機序: `shutil.rmtree(tmp, ignore_errors=True)` が Windows で **read-only 属性の git object を削除できず、`ignore_errors=True` が失敗を無音にする**。
  git object は `git` が read-only で書くため、git リポを作る検査(C11・C14)で必ず起きる。独立検査官環境(Git ownership 制約)では削除も policy で拒否され残置。
- 検出経路: ECO-064 r1 検査官の「後片付け拒否」報告(2026-09-11)→ 受理側の grep で 281 件 → 本起票で 350+11 件。**製造者環境では 40 日間・数百回の実行で誰も観測しなかった**
  (温度計のない fail-silent — 無音は無報告と同じ・「空白は無報告のみが悪」)。

### 0.2 同型の箇所(self-conformance.py・実読)

`shutil.rmtree(..., ignore_errors=True)` は **8 箇所**: t4 selftest(:262)/ C4 scaffold(:335)/ C11(:399)/ gu(:518)/ C13(:652)/ C14(:736)/ C15(:798)/ trx(:1112)。
残置が実測されているのは git リポを作る C11・C14 のみ(他は read-only ファイルを作らない)が、同型の無音は 8 箇所すべてにある。
他ツール: `effort-calibration.py:361`・`ui-cad-gate.py:139` も `ignore_errors=True`(本 ECO の範囲外・OBS-20260911-02 の 3 例目候補として記録)。

### 0.3 なぜ自己検査が捕捉しなかったか

- 後片付けは検査の判定に関与しない(`finally` 節)。判定器は「検査対象の tree」しか見ず、自分の副作用(temp)を測らない — playbook §13「計器は自分の前提を
  自分で満たす」の環境軸の逆(自分の後始末を自分で確認しない)。
- 陽性対照がない: read-only ファイルを含む temp が消えることを測る腕は 0。

### 0.4 起票工程の job 経由起動(Phase 4 の 3 本目候補)

- register 追記直後に `python method/tools/bomdd-job.py ECO-065` を実行(§preflight receipt に出力を記録)。ECO-064 verified 後のため `required_skills` は
  **非 null**(activation-map: start+instrument-change〔affected_refs= method/tools/self-conformance.py〕→ preflight・calibrate)— 明示起動の初例。

## 1. 変更要求(製造対象の候補 — 製造裁定時に凍結)

1. **共通 helper** `_cleanup_tmp(tmp) -> list[str]`(self-conformance.py 内): `shutil.rmtree` を `onexc`(Python 3.12+)/ `onerror` で受け、read-only を
   `os.chmod(path, stat.S_IWRITE)` で外して再試行。それでも消せないパスを**戻り値で返す**(無音にしない)。8 箇所の `rmtree(ignore_errors=True)` を helper に置換。
2. **報告**: 残置があれば `[cleanup] 残置 N 件: <paths>` を**必ず**出力(stderr)。判定への影響= **候補 2 案**(製造裁定): (A) 警告のみ・exit 不変(後片付けは適合性判定
   ではない・pre-push を止めない)/ (B) 残置を不適合として FAIL(fail-closed・「無音は無報告」の徹底)。当方案= **A**(判定は検査対象の tree にのみ依存させる— C18 witness の
   意味を保つ・残置は環境事象であり方法論の不適合ではない)。ただし**警告を出したことを selftest で測る**(温度計を持つ)。
3. **陽性対照**(selftest): read-only ファイルを含む temp を作り helper が空にすること・削除不能(open handle / 権限)を模した temp で残置パスが返ることの 2 腕。
4. **既存残置の掃除**: c11 350 件(1,154 MB)は製造時に当方が削除(製造裁定で確認)。sandbox 所有分は利用者へ報告。
5. **採らない**: `ignore_errors` の単純削除(traceback で検査が落ちる= 新たな fail-closed だが後片付けで判定が変わる)/ 他ツール(effort-calibration・ui-cad-gate)への同時適用
   (別 ECO・OBS-20260911-02 の 3 例目待ち)/ temp を作らない設計変更(検査の性質上 git リポが要る)。

## 2. 影響なし予測(起票段階・反証可能)

起票の diff は台帳系のみ。製造時(候補): self-conformance.py の変更は `finally` 節と helper 追加に限られ、**C1〜C18 の判定は不変**(判定入力は検査対象の tree のみ)。
`[cleanup]` 行が標準エラーに増える(標準出力の PASS 行は不変)。pre-push witness の形式・C18 不変。CI(ubuntu/windows)で読み取り属性の扱いが異なるため windows で
残置 0 件になることを CI ログで確認する。他ツール・templates・hooks は diff 0。

## 3. 受入(製造時の候補)

- **V1**: selftest の陽性対照 2 腕 PASS(read-only を含む temp が消える / 削除不能で残置が返る)。**V2**: self-conformance 実行後に `%TEMP%` の `bomdd-selfconf-*` が
  実行前より増えない(前後の件数を実測・windows)。**V3**: 全検査の判定不変(C1〜C18 PASS のまま)。**V4**: CI 緑(windows job のログに `[cleanup]` 残置なし)。**V5**: diff 窓。
- 独立検査: 機械挙動(計器の後片付け)の変更だが判定に関与しない → **製造者較正のみで受入**を当方案とする(裁定 B を採る場合は判定に関与するため異系統必須)。

## /preflight receipt(起動経路: **job 経由** — `bomdd-job.py ECO-065` の出力を開始 artifact として読んだ〔§0.4〕)

- 分類= 既裁定の適用実装(user 裁定 2026-09-11「起票して」)。baseline `689a219`= **confirmed**(HEAD・作業木 clean)/ 次番 065= **confirmed**(register 末尾= 064)/
  残置の実在= **confirmed**(§0.1 実測)/ 8 箇所の同型= **confirmed**(grep)/ 凍結の非該当= **confirmed**(converge・calibrate 非接触)/ 同一ファイルへの進行中 ECO なし=
  **confirmed**(self-conformance.py を対象とする in-progress ECO なし)。
- job ビュー(起票直後): `required_skills`= [calibrate, preflight](start / instrument-change)・`skills_observed`= [preflight, converge](本 receipt と下記 converge receipt)・
  `skills_missing`= [calibrate](verified 昇格時に埋まる)— **明示起動の初例**: job が preflight を要求し、本 receipt で応じた。
- 開始判定: **PROCEED**(起票まで)・override 0。製造は別裁定。

## /converge receipt(起動経路: 自発 — 是正案の設計〔判定への影響 A/B〕)

- **判定: 収束**(round 軌跡: 3→1→0→0)。
- DoD: ✔ 無音を無くす(残置を必ず報告)/ ✔ 判定(C1〜C18)を後片付けに依存させない案を第一候補にし、依存させる案を対置する / ✔ 陽性対照を持つ / ✔ 8 箇所を共通 helper に
  まとめる(列挙でなく構造)/ ✔ 他ツールは範囲外と宣言。
- round 1(新規 3 件): ①`ignore_errors` を外すだけでは traceback で検査が落ち、後片付けで判定が変わる → helper で捕捉して報告へ ②git object の read-only は `onerror` で
  chmod → 再試行が定石(Windows)③残置の扱い A/B は裁定点 → §1-2 に対置。
- round 2(新規 1 件): 「警告を出した」こと自体を測る腕がないと温度計が無音になる → selftest の陽性対照に「残置パスが返る」腕を追加(§1-3)。round 3: 0 件。round 4: 0 件。
- 検証した主張: 8 箇所の所在(grep・行番号)/ 残置の中身が read-only の git object(`ls -l`)/ 発生率(直近 1 回の前後)/ 他ツールの同型(grep)。
- 敵対自問: 「fail-closed を徹底するなら B では」— 後片付けは検査対象の性質でなく環境の性質。B にすると環境差(sandbox 所有・権限)で判定が赤くなり、C18 witness が
  「方法論の適合」を意味しなくなる。A+温度計(警告の陽性対照)で無音を消し、判定の意味は保つ。「helper 化で 8 箇所の挙動が揃うのは過剰変更では」— 同一文 8 箇所は列挙の腐敗
  そのもの(§13 原則⑥)。
- 未収束事項: なし(A/B は製造裁定の入力)。
