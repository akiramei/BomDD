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

## 4. 製造裁定と製造(2026-09-11・user「ECO-065 の製造まで進めて(A 案で)」)

- 製造裁定: **A 案**(残置は警告のみ・判定 C1〜C18 不変)。製造範囲(凍結)= §1 候補 1〜4。allowed_paths= `method/tools/self-conformance.py`+台帳系。
  独立検査= §3 の当方案どおり**製造者較正のみで受入**(A 案は判定に関与しない後片付けの変更)。
- 起動: **job 経由**(`bomdd-job.py ECO-065` → state=filed・stop_type=NONE・`required_skills`= [calibrate, preflight]〔start+instrument-change〕・observed= [preflight,
  converge]・missing= [calibrate])。preflight(製造着手): baseline `6cf654b`= confirmed(HEAD・clean)/ 8 箇所の所在= confirmed(grep 8/8)/ `check()`・`main()` の要約経路=
  confirmed(実読)/ 凍結の非該当= confirmed。PROCEED。

## 5. 製造物(`method/tools/self-conformance.py`・+86/-8 行)

- `_cleanup_tmp(tmp) -> list[str]`: `shutil.rmtree` を `onexc`(3.12+)/`onerror` で受け、`os.chmod(path, S_IWRITE)` → 再試行。それでも消せないパスと、削除後に
  なお存在する tmp を戻り値で返し `CLEANUP_RESIDUE` に集約(無音にしない)。**8 箇所**の `rmtree(tmp, ignore_errors=True)` を置換(t4・C4・C11・gu・C13・C14・C15・trx)。
- `_cleanup_selftest()`: 陽性対照 **3 腕** — ①read-only ファイルを含む temp が消える ②open handle(Windows)で削除不能 → 残置が返り temp が残る ③handle 解放後に消える。
  posix では②③を「対照不可」と宣言。較正で意図的に作った残置は本番の残置に数えない(`CLEANUP_RESIDUE` を復元)。
- **C14 の較正行**: `c14_kit_freshness()` の冒頭で `_cleanup_selftest()` を `check("C14", ...)` として出す — helper が壊れていれば**計器欠陥として FAIL**(較正)。
  残置そのものは判定に関与しない。
- **main 末尾**: `[cleanup] 残置 N 件(判定不変・ECO-065 A 案): <paths>` を stdout と stderr の両方に出力(0 件でも `[cleanup] 残置 0 件` を出す= 温度計を常に見せる)。
  終了コードと witness 書出しの条件は不変。
- `import stat` を追加。既存 C 検査の判定式・メッセージは不変(C14 に較正行が 1 行増えるのみ)。

## 6. 受入の実測(製造者・2026-09-11)

- **V1**= PASS(陽性対照 3 腕: 単体実行で `read-only 消去=True・削除不能で残置が返る=True・解放後に消える=True`。入れ子の read-only〔`a/.git/objects/ab/cdef`〕も
  残置 0 で消えることを追加実測。self-conformance 本番でも `[C14] PASS cleanup 較正 ...` として観測)。
- **既存残置の掃除**: 実行前に `bomdd-selfconf-*` 363 件(c11 350・c14 11・他 2)のうち **351 件を削除**(read-only 属性を外して再帰削除)。残り **12 件は sandbox 所有**
  (独立検査官の実行が作成・当方の権限では不可・利用者の削除に委ねる: c11 6 件・c14 6 件)。
- **V2**= PASS(self-conformance 実行前 12 件 → 実行後 12 件・増加 0。`[cleanup] 残置 0 件`)。**是正前は 1 回あたり c11 1+c14 2 件が増えていた**(§0.1)。
- **V3**= PASS(全検査 PASS・FAIL 0・PASS 行 20 → 21〔C14 較正行の追加分のみ〕・kit-freshness 7/7 不変・stderr 出力なし)。
- **V4**(CI)・**V5**(窓)・witness → §7。

## 7. クローズ(2026-09-11・verified)

- **witness 遷移**: §4〜§6 記入後に self-conformance を再実行(exit 0)→ `bomdd-witness.py produce --eco ECO-065` → `verify --eco ECO-065`= ADVANCE → fix commit `a2f9e41127f801a5cb603483f09a53dcaf8ad60b`。
- **V4**= PASS(CI run 34514888608・success・headSha a2f9e41127f801a5cb603483f09a53dcaf8ad60b 一致・3 job。windows job のログで `[cleanup] 残置 0 件` を確認= 残置 0 件・較正 3 腕 True〔ubuntu は posix 対照不可・残置 0 件〕)。
- **V5**= PASS(窓 `689a219` → `a2f9e41127f801a5cb603483f09a53dcaf8ad60b`= allowed_paths のみ: self-conformance.py+台帳系。他ツール・templates・hooks の diff= 0 — 影響なし予測が的中)。
- diff 監査の窓: baseline `689a219` → head `a2f9e41127f801a5cb603483f09a53dcaf8ad60b`(**窓閉鎖**)。本クローズ commit は台帳系(order・register・improvements.md・ECO-062 order)のみ。
- **製造者較正のみで受入**(A 案・§3/§4 の宣言どおり。異系統独立検査なし — B 案へ切り替える場合は判定に関与するため異系統必須)。
- **register**: `implemented → verified`・head 凍結。
- **Phase 4 の 3 本目としての帰結**(ECO-062 §7 へ反映): job 経由の起動・witness 遷移は成立(逸脱 0)。**EXP-20260910-01 の 2 例目**(required_skills 非 null の初例):
  job が preflight・calibrate を要求 → preflight は起票時の receipt で応答(missing [calibrate])→ verified 昇格の較正 receipt(下記)で missing [] へ。converge は要求外だが
  A/B 案の設計で自発起動(observed に含まれる)。非起動 0。

### 較正 receipt(/calibrate 自己適用 — trigger ①: verified 昇格+③: 計器〔self-conformance の後片付け helper・C14 較正行〕の変更。二軸)

- 査定した主張と判定:
  1. 「8 箇所の無音な rmtree が helper に置換され、残置は必ず報告される」— **observed / 適格**(grep で `ignore_errors` 0 件・`_cleanup_tmp(tmp)` 8 件。本番で `[cleanup] 残置 0 件` 行を観測)。
  2. 「helper は read-only の git object を消せる」— **observed / 適格**(陽性対照 3 腕 PASS・入れ子 read-only の追加実測・本番実行前後で temp 件数 12 → 12)。
  3. 「削除不能は残置として返る(無音でない)」— **observed / 適格**(陽性対照②: open handle で残置が返り temp が残る・③: 解放後に消える。posix では対照不可を宣言)。
  4. 「判定 C1〜C18 は不変」— **observed / 適格**(PASS 行 20 → 21 の差は C14 較正行のみ・FAIL 0・kit-freshness 7/7・終了コード条件と witness 書出し条件は不変〔コード読解〕)。
  5. 「CI(ubuntu)でも残置 0 かつ判定不変」— **observed / 適格**(CI 3 job success)。ただし ubuntu の read-only 挙動は windows と異なる(posix は read-only でも削除可)ため、
     本 ECO の主張の中心は windows job で観測した。
  6. 「A 案で C18 witness の意味(方法論の適合)が保たれる」— **読解**(残置は FAILURES に入らず witness 条件は不変。sandbox 所有の残置 12 件がある環境でも本番 PASS を観測= 環境事象が判定を汚さない実例)。
  7. 「他ツール(effort-calibration・ui-cad-gate)の同型も直っている」— **unknown(範囲外・OBS-20260911-02 の 3 例目待ち)**。
- 検出した計器欠陥(帰属つき): 製造物 0 件(本 ECO は計器の後片付けの是正)。是正前の計器欠陥= 温度計のない fail-silent(8 箇所・製造物帰属・§0)。受理側 0 件。
- 検出力の限界: 陽性対照は当方の環境(Windows・NTFS)での実測。posix の削除不能腕は対照不可。sandbox 所有の残置(12 件)は当方の権限では削除も再現もできない。
  `onexc` 経路は Python 3.12+ のみ実測(3.11 以下の `onerror` 経路は未実測・宣言)。
- battery 行別記録:

  | Q | asked/NA | 判定 | 実測 or 読解 | 所見 |
  |---|---|---|---|---|
  | Q1 | asked | observed/適格 | 実測 | helper の自己記述(消せる・返す)を陽性対照 3 腕で実測 |
  | Q2 | asked | observed/適格 | 実測 | known-good(read-only が消える)と known-bad(open handle で残置)を対で持つ |
  | Q3 | asked | observed/適格 | 実測 | 是正前の残置発生(1 回あたり 3 件)と是正後の 0 件を前後で実測 |
  | Q4 | asked | observed/適格 | 実測 | 陽性対照は実 temp・実 rmtree・実 chmod を入力(モックなし) |
  | Q5 | asked | observed/適格 | 実測 | sandbox 所有 12 件は削除不能と明記・posix 腕は対照不可と宣言・3.11 以下は未実測と宣言 |
  | Q6 | asked | observed/適格 | 実測 | 検査 exit 観測 → witness produce/verify(条件結合)→ commit → push → CI 照合 |
  | Q7 | asked | observed/適格 | 実測 | 陽性対照= C14 較正行(本番で毎回実行) |
  | Q8 | NA | — | — | 免除機構なし |
  | Q9 | asked | observed/適格 | 実測 | witness(個体+tree)・register・commit で来歴化 |
  | Q10 | asked | 宣言 | 読解 | 上記「検出力の限界」+主張 7 の unknown |
  | Q11 | asked | observed/適格 | 読解 | 入力クラス= read-only ファイル / 入れ子 read-only / open handle / posix / sandbox 所有(削除不能・対照不可)/ 3.11 以下(未実測) |

- このクローズが支持しないもの: 他ツールの同型(範囲外)/ posix の削除不能挙動 / Python 3.11 以下の `onerror` 経路 / sandbox 所有の残置の削除 /
  B 案(残置を FAIL)の是非(A 案の裁定で閉じた— 再開条件= 残置が方法論の適合に影響した実測)。
