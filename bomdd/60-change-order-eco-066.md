# Change Order — ECO-066(bomdd-witness の検証報告を運転員が機構で読める形にする — 理由コード・個体照合の既定化・tree 差分表示・測定不能の原因分離〔verified〕)

> 裁定: user 2026-09-11 Phase 5 DECIDE `1:C 2:A` — Phase 6 を保留し、**検証器の是正 ECO を先に閉じてから運転員を変えた run-02** を実施する(1:C)。
> ECO の範囲は**検証器のみ**(2:A・停止語彙は増やさない)。出典= [ECO-062 order](60-change-order-eco-062.md) §10.4 所見 P5-01/02/03/06/07・
> [Phase 5 run 台帳](reports/phase5-run-01-eco-062.md) §6。**起票のみ**(製造着手・範囲の凍結は別裁定)。起票工程は job 経由(§0.4)。

## 担当設備(equipment)

- 起票: requested/resolved `claude-fable-5-1`・Claude Code(Claude Agent SDK)・来歴 **self-reported**

## 0. 実測(起票根拠 — Phase 5 run-01・運転員= Codex・2026-09-11)

### 0.1 検証器の報告が運転員に届いていない(実読・run 台帳 §3/§4/§6)

| 所見 | 実測 | 座標 |
|---|---|---|
| P5-01 理由が機械可読でない | 検証器は STOP+理由**文**を返すが停止種別を返さず、運転員が VERIFICATION_FAIL / MISSING_INPUT へ自前写像した(運転員申告) | `bomdd-witness.py` verify:164-196(文字列 6 種)・run 台帳 §3 手順の欠落 1 |
| P5-02 個体照合が既定でない | `verify PATH` 単独は個体を照合せず、別 job の receipt(R3)が **ADVANCE exit 0** になる。運転員は `--eco` 付き掃引を**自発的に**追加して STOP に至った(機構でなく判断) | usage :25 は `verify [PATH \| --eco ECO]`・main :384-400 は PATH と `--eco` の併用を受理するが文書化なし・run 台帳 §2 R3・§6 P5-05 |
| P5-03 不一致箇所が見えない | R6(末尾 4 桁改変)の理由文が `witness 0ddfd1dbacfc / 現 0ddfd1dbacfc` と同一に見える(12 桁接頭辞) | verify :178 `[:12]` |
| P5-06 測定不能の原因が分離されない | run-02 で sandbox 内の検証器が `現 tree を取得できない(git 不能または一時 index 不能)` を返したが、git 不能か temp 不能か `add -A` 失敗かを区別できない。推定機序(sandbox の `.git/objects` 書込拒否)が実測できない | worktree_tree :79-105 は 5 経路で None を返し理由を捨てる・verify :174 |
| P5-07 実行基盤が exit 2 を 1 に丸める | Codex(Windows)の `pwsh -Command` は非 0 終了を 1 に丸める(当方で再現)。3 値契約(0/1/2)が終了コードでは届かず、運転員は文言から不一致を申告した | run 台帳 §6 P5-07・§4 |

- 帰結: run-01 の fail-open 0/7 のうち 2 件(R3・run-02)は**運転員の判断**で成立しており、検証器単独の弁別力ではない(qualification blocker・ECO-062 §10.5)。

### 0.2 触らないもの(実読)

- pre-push hook は `.git/bomdd-selfconf-witness`(2 行)を読み、本ツールの witness(`.git/bomdd-witness/<ECO>.json`)は読まない(W4)→ 非接触。
- `bomdd-job.py` は `bomdd-witness.py` を import しない(実読: import は self-conformance の定数のみ)→ 非接触。停止語彙(W3・job と共通の固定値)は増やさない(2:A)。
- selftest は関数 `verify(root, path, eco=None)` を eco なしで多用する → 関数の省略可能性は残し、**CLI だけ**を既定化する。

### 0.3 P5-04 / P5-07 の手順側(本 ECO の範囲外)

運転員が AGENTS.md 由来で preflight/calibrate を読みに行く(P5-04)・終了コードと文言の突合(P5-07 の手順側)は**ブリーフ v2**(run-02 の準備・記録物・ECO 外)。
本 ECO は P5-07 の**計器側**緩和(1 行目で 3 値が読める)のみを持つ。

### 0.4 起票工程(job 経由)

起票前の job ビュー(`bomdd-job.py ECO-066`)は register 追記後に出力し、required_skills / skills_missing を /preflight receipt に記す(ECO-065 と同じ手順)。

## 1. 変更要求(製造対象の候補 — 製造裁定時に凍結・対象= `method/tools/bomdd-witness.py` のみ)

1. **報告形式の固定(P5-01・P5-07 計器側)**: 標準出力の 1 行目を `<VERDICT> <CODE>[(<CAUSE>)]: <message>` に固定する。VERDICT= `ADVANCE` / `STOP` / `UNMEASURABLE`
   (終了コード 0 / 1 / 2 と 1 対 1・終了コードは不変)。CODE の語彙(固定・witness 側ローカル・job の停止語彙とは別物): `OK` `IDENTITY_MISMATCH` `IDENTITY_UNCHECKED`
   `TREE_MISMATCH` `GATES_MISSING` `GATE_INCOMPLETE` `GATE_FAIL` `STOP_TYPE` `WITNESS_UNREADABLE` `WITNESS_MALFORMED` `TREE_UNAVAILABLE` `ARG_ERROR`。
   運転員は終了コードが丸められても 1 行目で 3 値と理由を機械的に読める。
2. **個体照合の既定化(P5-02)**: CLI の `verify PATH` で `--eco` が無い場合は `UNMEASURABLE IDENTITY_UNCHECKED` exit 2(個体未照合は合格ではない)。
   `verify --eco X`(既定パス)と `verify PATH --eco X` は従来どおり照合する。usage 行に `verify PATH --eco ECO`(個体照合・必須)を明記。関数 `verify(eco=None)` は
   selftest 用に残す。
3. **tree 差分の表示(P5-03)**: `TREE_MISMATCH` の message は両 tree を **40 桁**で示し、最初に異なる位置(0 起点)を添える。
4. **測定不能の原因分離(P5-06)**: `worktree_tree` が None を返す 5 経路を CAUSE で区別する — `GIT_UNAVAILABLE` / `GIT_DIR_FAILED` / `TEMP_UNAVAILABLE` /
   `TEMP_IN_WORKTREE` / `ADD_FAILED` / `WRITE_TREE_FAILED` — と、git の stderr 末尾 1 行を message に含める。run-02 で「sandbox の `.git` 書込拒否」の推定を実測に変える。

**採らない**: 停止語彙(job と共通)への `RECEIPT_INVALID` 追加(2:A)/ `bomdd-job.py`・pre-push hook・self-conformance への接触 / 検査の再実行(W2 の申告値の再実測は
受入側の責務)/ `--json` 出力(1 行目の固定で足りる — 必要が実測されてから)/ 終了コードの意味変更(0/1/2 は不変)/ P5-04・P5-07 の手順側(ブリーフ v2・ECO 外)。

## 2. 影響なし予測(起票段階・反証可能)

起票の diff は台帳系のみ(本 order・register・ECO-062 order §7 現在地・improvements.md の EXP 注記)。製造時(候補): 変更は `bomdd-witness.py` のみ。
**挙動が変わるのは 1 点だけ**= CLI `verify PATH`(`--eco` なし)が 0/1 → 2。利用箇所は Phase 5 の運転員手順と selftest のみ(実読)。pre-push hook(別 witness・W4)・
`bomdd-job.py`(import なし)・self-conformance C1〜C18(検査対象集合に本ツールは入らない — C5a/b は名指し 2 スクリプト・C4 scaffold は kit 非含有)は判定不変。
製品リポ非波及(kit に含まれない)。終了コードの意味は不変。

## 3. 受入(製造時の候補)

- **V1**(陽性対照): `--selftest` に CODE ごとの腕を持つ(12 CODE・`TREE_UNAVAILABLE` は CAUSE 別に再現できる範囲= GIT_UNAVAILABLE〔PATH 空〕・TEMP_IN_WORKTREE・
  TEMP_UNAVAILABLE〔TMPDIR 不能〕)+ `verify PATH` 単独 → exit 2 の腕 + 既存腕の期待 1 行目を更新。
- **V2**(run-01 治具の再判定): `.git/bomdd-witness/phase5/r1〜r8.json` を `--eco` 付きで再検証し、期待 CODE 表(製造時に固定・現 tree は run-01 時と異なるため
  tree 束縛の腕は TREE_MISMATCH)と一致。R6 で差分位置 36 が出る。
- **V3**(不変): pre-push witness の 2 行形式と hook の読取不変・`bomdd-job.py` diff 0・self-conformance 全 PASS・判定不変。
- **V4**: CI 緑・窓= `bomdd-witness.py`+台帳系。
- **V5**(異系統独立検査): instrument-change のため **Codex(異系統・CLI 直接)必須**(ECO-062 §4 裁定 3 の型)。受理側の真正判定を order に記録してから verified。
- **V6**(運転員視点・計器側): `pwsh -Command` 経由で exit が丸められる条件下でも、1 行目から VERDICT/CODE が読めること(当方環境で pwsh 経由の実測 3 値)。

## /preflight receipt(起動経路: **job 経由** — `bomdd-job.py ECO-066` の出力を開始 artifact として読んだ〔§0.4〕)

- 分類= 既裁定の適用実装(user DECIDE `1:C 2:A`・起票まで)。baseline `b268f37`= **confirmed**(HEAD・作業木 clean)/ 次番 066= **confirmed**(register 末尾= 065)/
  所見の座標= **confirmed**(`bomdd-witness.py` :25/:79-105/:164-196/:384-400 と run 台帳 §3/§4/§6 を実読)/ 非接触の根拠= **confirmed**(pre-push hook の読取先・job.py の
  import を実読)/ 凍結の非該当= **confirmed**(converge・calibrate 非接触)/ 同一ファイルへの進行中 ECO なし= **confirmed**(in-progress は ECO-055 のみ・refs 非重複)。
- job ビュー: required_skills= `["calibrate", "preflight"]`(start + instrument-change〔affected_refs `method/tools/*.py`〕)・skills_missing(起票時)= `["calibrate"]`
  (calibrate は verified 昇格時の較正 receipt で応答する— ECO-065 と同じ軌跡)。
- 開始判定: **PROCEED**(起票まで)・override 0。製造は別裁定。

## /converge receipt(起動経路: 自発 — 報告形式と既定化の設計〔§1 の 4 項〕)

- **判定: 収束**(round 軌跡: 3→1→0)。
- DoD: ✔ 4 所見(P5-01/02/03/06)が各 1 項の変更要求に写る / ✔ 停止語彙を増やさない(2:A)/ ✔ 終了コードの意味不変 / ✔ 挙動変更は 1 点に限定し利用箇所を実読で列挙 /
  ✔ 非接触(hook・job・self-conformance)を実読で裏取り / ✔ P5-07 の計器側と手順側を分離。
- round 1(新規 3 件): ①`verify PATH` を「STOP 個体未照合(exit 1)」にする案は、STOP= 「receipt が無効」と意味が混ざる → 個体未照合は**測定不能(exit 2)**へ(「測定不能は
  合格ではない」の型)②selftest が `verify(eco=None)` を多用 → 関数は省略可のまま・CLI のみ既定化 ③CODE を job の停止語彙に混ぜると W3(共通固定値)が崩れる →
  witness ローカルの語彙と明記。
- round 2(新規 1 件): 差分表示を「最初に異なる位置」だけにすると人間が読めない → 40 桁両方+位置。
- round 3: 新規 0。**未収束事項: なし**。

## 記録(起票時)

- register: `filed`(2026-09-11)・baseline `b268f37`・allowed_paths(起票段階)= 台帳系+`bomdd-witness.py`(製造裁定で再凍結)。
- ECO-062 §7 現在地= 「ECO-066 起票済・製造裁定待ち → verified 後に run-02(運転員変更・ブリーフ v2)」。EXP-20260910-02 の next trigger を同じく更新。
- **次の裁定(製造裁定)**: 範囲= §1 の 4 項をそのまま凍結するか(当方案= そのまま)・独立検査= Codex(V5)。

## 4. 製造裁定と製造(2026-09-11・user DECIDE「A」— §1 の 4 項をそのまま凍結・独立検査= Codex)

- register `filed → decided`(同日)。affected_refs= `method/tools/bomdd-witness.py` で凍結。allowed_paths= 製造物 1+台帳系+検査報告。影響なし予測(製造前・凍結)は register。
- 製造者= Claude Code(claude-fable-5-1・起票者と同一)。独立検査= Codex(異系統・CLI 直接・§3 V5)— verified は検査官の受理側真正判定を §7 に記録してから。

## 5. 製造物(`method/tools/bomdd-witness.py`・+232/-101 行・541 行)

| §1 | 実装 |
|---|---|
| 1 報告形式 | `VERDICTS` / `CODES`(12)/ `TREE_CAUSES`(6)の定数と `report_line(rc, code, msg, cause)`。`_verify()` が `(rc, code, cause, msg)` を返し、`verify()` は従来の `(rc, 1 行目)` を返す(selftest の呼び出し互換)。CLI は `run_cli(argv, root) → (rc, 1 行目)` に分離し `main` は印字のみ(selftest が CLI 腕を in-process で回せる) |
| 2 個体照合の既定化 | `run_cli` の verify 分岐で `--eco` なし(PATH 指定・`--out` 指定とも)は `UNMEASURABLE IDENTITY_UNCHECKED` exit 2。`verify --eco X`(既定パス)と `verify PATH --eco X` は従来どおり。関数 `verify(eco=None)` は残す。usage(冒頭 W7)に明記 |
| 3 tree 差分 | `_first_diff(a, b)`= 最初に異なる位置(0 起点・長さ違いは短い方の長さ・同一なら「なし」)。`TREE_MISMATCH` の message は両 tree 40 桁+`最初の差分位置 N`。witness.tree が文字列でなければ `n/a` |
| 4 原因分離 | `worktree_tree()` の返り値を `(tree, git_dir, err)` に拡張。err= `(CAUSE, detail)`: rev-parse 失敗(rc 127 → GIT_UNAVAILABLE / 他 → GIT_DIR_FAILED)・TemporaryDirectory の OSError → TEMP_UNAVAILABLE・作業木内 temp → TEMP_IN_WORKTREE・add 失敗 → ADD_FAILED・write-tree 失敗 → WRITE_TREE_FAILED。detail= git stderr 末尾 1 行(`_tail`・200 字)。produce / verify / 既定パス導出の 3 呼び出し元を更新 |

- 終了コードの意味(0/1/2)は不変。1 行目以外の出力は変えていない(verify は 1 行のみ・produce の成功行は従来どおり)。
- selftest: 既存腕はすべて **CODE(と CAUSE・文言)まで検査**する `arm()` に置換(終了コードだけの検査から、運転員が読む経路の検査へ)。追加腕= 差分位置 36 / 0・tree 非文字列・
  形状不正(`[]`)・CLI 4 腕(PATH 単独 → IDENTITY_UNCHECKED・`--eco` 付き 0・既定パス 0・`--out` 単独 → IDENTITY_UNCHECKED)・引数不正 6 型 → ARG_ERROR・
  CAUSE 6 種(GIT_UNAVAILABLE= PATH 空 / TEMP_UNAVAILABLE= tempdir 不在 / TEMP_IN_WORKTREE= tempdir を作業木に / ADD_FAILED・WRITE_TREE_FAILED・GIT_DIR_FAILED=
  `_git` を差し替えて当該サブコマンドのみ失敗させる〔モック・宣言〕)・report_line の自己整合 4 腕・語彙外 CODE の検出。
- 製造中の実測(正直記載): 当初 §3 V2 に「R6 で差分位置 36」と書いたが、現 tree は run-01 時と異なるため R6 は差分位置 0 になる(下記 V2)。位置 36 の対照は selftest の
  kb-hash 腕が持つ。手順逸脱: なし(製造物は Write・CR 0・検査と commit は別呼び出し)。

## 6. 受入の実測(製造者・2026-09-11)

- **V1**= PASS: `--selftest` exit 0(CODE 12/12・CAUSE 6/6 に各 1 腕以上・CLI 4 腕・引数不正 6 型・差分位置 36 と 0)。
- **V2**= PASS: run-01 治具 r1〜r8 を `--eco` 付きで再判定 — r3= `STOP IDENTITY_MISMATCH`(個体照合が tree 照合より先)・他 7 本= `STOP TREE_MISMATCH`(現 tree `53bd2886…` は
  run-01 時 `0ddfd1db…` と異なる・40 桁両方と差分位置を表示・R6 は位置 0)。r3 を `--eco` なしで= `UNMEASURABLE IDENTITY_UNCHECKED` exit 2(run-01 では ADVANCE exit 0 だった
  fail-open 経路が閉じた)。
- **V3**= PASS: `bomdd/hooks/`・`bomdd-job.py`・`self-conformance.py` diff 0(実測)。self-conformance 全 PASS は §7(fix commit 前に再実行し exit を観測)。
- **V6**= PASS(計器側): `pwsh -NoProfile -Command 'python … verify …'` で終了コードは実際 2 でも 1 でも **1** に丸められた(再現)が、標準出力 1 行目は
  `UNMEASURABLE IDENTITY_UNCHECKED: …` / `STOP TREE_MISMATCH: …` で 3 値が読める。`exit $LASTEXITCODE` を付けても本環境では 1(pwsh の `-Command` 文字列内では
  ネイティブ終了コードが伝播しない場合がある — 実行基盤側の事象・本 ECO の範囲外・ブリーフ v2 で「終了コードでなく 1 行目を読む」を規格にする根拠)。
- **V4**(CI)・**V5**(Codex 独立検査)= §7。

## 7. 独立検査(Codex・異系統・CLI 直接・workspace-write)

### 7.1 r1(2026-09-11・対象 commit `4068029`)= **REJECT**(IA-01〜03・付随 IA-04)— 報告: [independent-inspection-eco-066.md](reports/independent-inspection-eco-066.md)

検査官は独自 fixture を OS temp に作って再実測し、リポジトリは変更していない(受理側で run 前後の `git status --porcelain` 空・write-tree 同一を確認)。

| 所見 | 受理側の真正判定 | 是正(r1b・同日) |
|---|---|---|
| IA-01 固定形式が全 CLI 経路に適用されていない(produce の成功/失敗行・`--selftest` の行が生文字列) | **CONFIRMED**。§1-1 は「標準出力の 1 行目」と書き、製造者が verify に限定して読んだ(§5 に「produce の成功行は従来どおり」と明記していた= 製造者の読みの狭さ)。運転員が produce を回す Phase 6 では同じ穴になる | produce の全経路を `report_line` へ(成功= `ADVANCE PRODUCED`・stop 不正/作業木内出力= `ARG_ERROR`・gate 不完全= `GATE_INCOMPLETE`・tree 不能= `TREE_UNAVAILABLE(CAUSE)`・書込不能= `WITNESS_UNWRITABLE`)。selftest の 1 行目も固定(PASS= `ADVANCE OK`・FAIL= `STOP SELFTEST_FAIL` exit 1)。CODES 12 → **15**(本 ECO で閉じる・W6 更新)。selftest 腕: produce CLI・produce 各 CODE・`_report_text` の形式・CODES 全 15 の report_line/_code_of 往復 |
| IA-02 `.git/index` の複製失敗(copy2 の OSError)を TEMP_UNAVAILABLE に誤分類 | **CONFIRMED**(判定の誤り= CAUSE)。try が TemporaryDirectory 生成と copy2 を同じブロックで包んでいた | TemporaryDirectory 生成だけを TEMP_UNAVAILABLE に、copy2 の OSError は新 CAUSE **INDEX_COPY_FAILED**(TREE_CAUSES 6 → 7)。selftest 腕: 別の一時 git リポで `.git/index` をディレクトリにして verify → INDEX_COPY_FAILED(実 fixture・モックなし) |
| IA-03 rc 127 だけで GIT_UNAVAILABLE と判定(起動できた git/ラッパーの 127 を誤分類・9009 型は逆) | **CONFIRMED**(判定の誤り= CAUSE)。本来の「git 不在」は `_git` の OSError → 番兵 `_GitUnavailable` で来る | GIT_UNAVAILABLE は **番兵の isinstance のみ**で判定(rev-parse / add / write-tree の 3 箇所)。起動できた git の rc 127 は GIT_DIR_FAILED 等+stderr 末尾。9009 型(ラッパーが「not recognized」)は GIT_DIR_FAILED+stderr で運転員に文言が届く(分類はできない— 宣言)。selftest 腕: `_git` を rc 127・stderr「executable ran」で差し替え → GIT_DIR_FAILED(GIT_UNAVAILABLE でない) |
| IA-04 `_git` が `text=True` のみで、非 UTF-8 の stderr で reader thread が UnicodeDecodeError を出し末尾行を失う | **CONFIRMED**(文言のみ・ただし traceback が stderr に漏れる) | `_RUN_KW = capture_output・text・encoding="utf-8"・errors="replace"` を `_git` に適用。selftest 腕: 同じ kwargs で `\x81\xff` を stderr に書く子プロセスを回し、例外なし・末尾行 `tail` が残ることを確認(git 自身が非 UTF-8 を出す個体は作れない— 検査官と同じ限界を宣言) |

- 検査官の追加確認(受理側で採用): 差分位置の境界値(短縮 39・延長 40・先頭 0・末尾 39・非文字列 n/a)、CLI 10 経路の exit と 1 行目、hook / job / self-conformance の非依存(実読)、
  W7 の設計判断(個体未照合= UNMEASURABLE)への反証なし、CODE と job 停止語彙の分離への反証なし(CODE → 停止語彙の写像は本ツール外= 運転員手順側・ブリーフ v2)。
- 検査官が測れなかったもの: self-conformance の全 C1〜C18(witness を書くため read-only ブリーフで未実行)→ 受理側で実行(§6 V3・§8)。`WRITE_TREE_FAILED` の実 git 障害(モックのみ)→ 宣言のまま。
- r1b 付随: `TemporaryDirectory(ignore_cleanup_errors=True)`— try を分割したことで後片付けの OSError が with ブロック外へ漏れる経路を塞ぐ(製造者が r1b で気づいた・検査官所見ではない)。
- r1b の受入: `--selftest` exit 0(1 行目 `ADVANCE OK: selftest PASS(...)`)・produce `--stop BOGUS` → `UNMEASURABLE ARG_ERROR: …`・r3 治具 `--eco ECO-062` → `STOP IDENTITY_MISMATCH: …`。self-conformance・CI・r2 は下記。

### 7.2 r2(2026-09-11・対象 commit `b39c6f7`・範囲= r1 所見の是正確認+回帰)= **ACCEPT** — 報告: [independent-inspection-eco-066-r2.md](reports/independent-inspection-eco-066-r2.md)

- IA-01〜04 の是正を検査官が独自 fixture で再実測(produce 5 経路の 1 行目・CODES 15 の語彙内・`.git/index` ディレクトリ → INDEX_COPY_FAILED・TemporaryDirectory への
  注入 → TEMP_UNAVAILABLE・rc 127 差し替え 3 種 → GIT_DIR_FAILED/ADD_FAILED/WRITE_TREE_FAILED・PATH 空 → GIT_UNAVAILABLE・非 UTF-8 stderr の子プロセス注入で例外なし・
  末尾行が置換つきで残る)。回帰: CLI 14 経路・差分位置の境界値 5 種・`ignore_cleanup_errors` の注入で判定不変・`git diff --check` 0。
- 検査官が採用しなかった証拠(受理側で評価): clean filter の `required=true` なしの試行は git が失敗を許容するため ADD_FAILED の証拠にしていない — 実 `add -A` 失敗の
  陽性対照は `required=true` で成立(モックでない実 git 障害の 1 例・製造者 selftest はモック)。
- 新規所見: なし。作業木汚染: 0(受理側で前後の porcelain 空・write-tree 同一)。検出力の限界(検査官宣言): 実 git バイナリの非 UTF-8 出力と cleanup の実 OS 故障は注入による確認。
- 受理側判定: **ACCEPT を採用**。r1 の 4 所見はすべて validator/分類器の入力クラスの穴(ECO-064 と同じ型)で、設計判断(W7・CODE の分離)への反証はなし。

## 8. クローズ(2026-09-11・verified)

- **witness 遷移**: 本 §8 と台帳の記入後に self-conformance を再実行(exit 0)→ `bomdd-witness.py produce --eco ECO-066` → `verify --eco ECO-066`= `ADVANCE OK` → accept commit。
- **V1**= PASS(selftest・CODE 15/15・CAUSE 7/7 に腕・r1b で実 fixture 2 腕追加)/ **V2**= PASS(run-01 治具の再判定・§6)/ **V3**= PASS(hooks・job・self-conformance・templates・
  .github の diff 0 を窓全体 `b268f37 → b39c6f7` で実測・self-conformance 全 PASS ×3)/ **V4**= PASS(CI 34560468428・34561713307 success)/ **V5**= PASS(Codex r1 REJECT → 是正 → r2 ACCEPT)/
  **V6**= PASS(pwsh 経由でも 1 行目で 3 値・§6)。
- diff 監査の窓: baseline `b268f37` → head `b39c6f7`(**窓閉鎖**)。窓内= `bomdd-witness.py`(+424/-122 相当・2 commit)+台帳系+検査報告 r1(r2 は本 commit で追加・allowed_paths を同一 commit で更新)。
  他ツール・templates・hooks・.github の diff= 0 — 影響なし予測(製造前・凍結)は的中。ただし予測の「挙動変更は 1 点」は r1b で produce/selftest の**出力形式**も変わったため
  under-inclusion(終了コードの意味は不変・出力 1 行目の形式のみ)。
- register: `implemented → verified`・head 凍結・allowed_paths に r2 報告を追加。
- Phase 5 への帰結(ECO-062 §7 現在地へ反映): R3 型(別 job の receipt)は運転員の判断でなく **機構**(CLI が個体未照合を測定不能にする)で止まる状態になった。
  次= 運転員を変えた run-02(ブリーフ v2= 「終了コードでなく 1 行目を読む」「AGENTS.md の自発起動は運転員の役割外」を規格化)。運転員の選定は user 裁定。

### 較正 receipt(/calibrate 自己適用 — trigger ①: verified 昇格+③: 計器〔bomdd-witness.py〕の変更。job の required_skills= [calibrate, preflight] に応答)

- 査定した主張と判定:
  1. 「CLI の全経路で 1 行目が固定形式」— **observed / 適格**(製造者 selftest+検査官 r2 の produce 5 経路・verify 14 経路・selftest 行。r1 で製造者の読みが狭かった穴を検査官が閉じた)。
  2. 「`verify PATH` 単独は測定不能(exit 2)になり、別 job の receipt を機構で止める」— **observed / 適格**(selftest・run-01 治具 r3・検査官 r1/r2)。
  3. 「tree 不一致は 40 桁+差分位置」— **observed / 適格**(境界値 5 種を検査官が独立に実測)。
  4. 「測定不能の 7 原因が正しく分類される」— **observed / 条件付き適格**(GIT_UNAVAILABLE・GIT_DIR_FAILED・TEMP_UNAVAILABLE・INDEX_COPY_FAILED・TEMP_IN_WORKTREE・ADD_FAILED は
     実 fixture か検査官の実 git 障害で実測。**WRITE_TREE_FAILED は製造者・検査官ともモックのみ**。9009 型ラッパーは分類できず stderr で伝える— 宣言)。
  5. 「終了コードの意味(0/1/2)は不変」— **observed / 適格**(検査官 r1 の baseline 差分読解+回帰 14 経路)。
  6. 「hooks・job・self-conformance は非接触」— **observed / 適格**(窓全体の diff 0・検査官の実読)。
  7. 「pwsh 経由で 1 行目から 3 値が読める」— **observed / 適格**(製造者環境で再現。**運転員環境〔Codex sandbox〕での実測は run-02 で**)。
  8. 「run-02 で fail-open 0 が機構として出る」— **unknown(未測定・run-02 の対象)**。
- 検出した計器欠陥(帰属つき): 製造物 4 件(r1 IA-01〜04・すべて製造者の selftest の未被覆枝・製造物帰属)。受理側 1 件(§3 V2 の「R6 で差分位置 36」は現 tree が
  変わる前提を見落とした受入基準の記述誤り・受理側帰属・§5 で訂正)。製造者の影響なし予測 1 件(出力形式の変更範囲を verify に限定して予測した under-inclusion・§8)。
- 検出力の限界: WRITE_TREE_FAILED の実障害は未実測。実 git の非 UTF-8 出力は未実測(注入のみ)。運転員環境での 1 行目の可読性は未実測(run-02)。selftest は製造者が書いた
  計器で、独立性は検査官の別 fixture 再実測の範囲まで。
- battery 行別記録:

  | Q | asked/NA | 判定 | 実測 or 読解 | 所見 |
  |---|---|---|---|---|
  | Q1 | asked | observed/適格 | 実測 | 製造物の自己記述(W6/W7)を selftest+検査官の独立 fixture で実測 |
  | Q2 | asked | observed/適格 | 実測 | known-good/known-bad を CODE ごとに対で持つ(15 CODE・7 CAUSE) |
  | Q3 | asked | observed/適格 | 実測 | 是正前(run-01: R3 が ADVANCE)と是正後(IDENTITY_UNCHECKED 2)を同一治具で前後実測 |
  | Q4 | asked | observed/条件付き適格 | 実測 | 実 temp・実 git を入力。git サブコマンド失敗 3 種は製造者側モック・検査官が ADD_FAILED を実 git で補完・WRITE_TREE_FAILED はモックのみ |
  | Q5 | asked | observed/適格 | 実測 | 未実測(WRITE_TREE_FAILED 実障害・実 git 非 UTF-8・運転員環境)を宣言 |
  | Q6 | asked | observed/適格 | 実測 | 検査 exit 観測 → witness produce/verify(条件結合)→ commit → push → CI 照合 ×3 |
  | Q7 | asked | observed/適格 | 実測 | 陽性対照= selftest(毎回)+検査官 r1/r2 の独立 fixture |
  | Q8 | NA | — | — | 免除機構なし |
  | Q9 | asked | observed/適格 | 実測 | witness(個体+tree)・register・commit・検査報告 2 本で来歴化 |
  | Q10 | asked | 宣言 | 読解 | 上記「検出力の限界」+主張 8 の unknown |
  | Q11 | asked | observed/適格 | 読解 | 入力クラス= CLI 引数の組合せ / witness の形状 / tree の型・長さ / git 起動不能・起動後失敗・index 複製失敗・temp 不能・temp 作業木内 / 非 UTF-8 出力 / 実行基盤の exit 丸め |

- このクローズが支持しないもの: 運転員環境(sandbox)での 1 行目可読性 / run-02 の fail-open / WRITE_TREE_FAILED の実障害分類 / 9009 型ラッパーの分類 /
  CODE → job 停止語彙の写像(運転員手順側・ブリーフ v2)/ 他ツールへの同型適用。
