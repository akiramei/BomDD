# Change Order — ECO-066(bomdd-witness の検証報告を運転員が機構で読める形にする — 理由コード・個体照合の既定化・tree 差分表示・測定不能の原因分離〔起票のみ〕)

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
