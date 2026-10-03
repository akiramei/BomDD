# Change Order — ECO-096(運転層の証跡ツール bomdd-witness.py が検査していない Git の木を束縛する — ECO-092 と同型の skip-worktree / assume-unchanged 未正規化の是正・selftest の CI 結線〔起票〕)

> 由来: ECO-092 §4「範囲外の発見」(2026-10-03)— `method/tools/bomdd-witness.py` の `worktree_tree` は実 index を一時 index へ複製して `add -A` する同じ機序を持ち、フラグ付き entry では index の bytes を束縛する。
> ECO-092 の凍結範囲外として記録のみとし、本 ECO で同じ正規化を適用する。標準の裁定= 2026-09-29「検査器の偽陰性は実害待ちにしない」・2026-10-03「2:A」(同クラスの偽陰性)。
> **起票のみ**。製造と異系統の独立検査(ECO-092 と同型・r1 境界探索+r2)の着手は裁定待ち(§5)。

## 担当設備(equipment)

- 起票: requested/resolved `claude-fable-5-1`・Claude Code(Claude Agent SDK)・来歴 **self-reported**
- producer: EQ-001
- inspector: EQ-002
  receipt が束縛する tree(運転層の ADVANCE / STOP の入力)を変える計器変更のため、異系統の独立検査を併用する(ECO-092 と同じ根拠)。workspace-write(一時 git リポが要る)。
  ECO-092 r2 の検査官環境は sparse-checkout(S/h entry 1151 件)だった— 本 ECO の対象状態がそのまま実在する環境であり、r1 ブリーフで「自環境の作業木で是正前後の tree を比較する」腕を置く。

## 0. 実測(起票根拠・2026-10-03)

- **機序**(`bomdd-witness.py` L115〜150 実読): `worktree_tree(root)` は `.git/index` を一時 index へ複製(`INDEX_COPY_FAILED` の分岐あり)→ `GIT_INDEX_FILE` で `add -A`(`ADD_FAILED` あり)→ `write-tree`(`WRITE_TREE_FAILED` あり)。
  **フラグの正規化が無い**。`git add -A` は skip-worktree(`S`)/ assume-unchanged(小文字タグ)の entry を更新しない(ECO-092 で再現・対照腕つき)→ 検査が読んだ作業ツリーでなく index の bytes を束縛する。
- **帰結**: W1「tree の定義は self-conformance C18 と同一」が ECO-092 以後は成り立たない(C18 は正規化する・本ツールはしない)。フラグ付き作業木では、受理側の `produce` と `verify` が同じ関数で自己整合するため機械は止まらないが、receipt が証明する bytes は検査していない index 側になる。
- **selftest の結線**: `bomdd-witness.py --selftest`(W1〜W7 の腕)は self-conformance にも CI(`.github/workflows`)にも結線されておらず、手動実行のみ(worklist.py の selftest は CI にある)。新しい腕を足しても毎 push では走らない。
- **露出**: 本リポの製造者環境は S/h 0 件。検査官 sandbox(ECO-092 r2)は 1151 件= 自然発生 1 例(受理側の環境ではない)。

## 1. 変更要求(製造対象の候補 — 製造裁定で凍結)

1. `worktree_tree`: 複製の後、一時 index に対して `ls-files -v -z` → `S` / 小文字タグの path を抽出 → `update-index --no-assume-unchanged -z --stdin` と `update-index --no-skip-worktree -z --stdin` を**別々の呼び出し**で(git 2.47 の無音の分岐・ECO-092 §4)→ `add -A` → `write-tree`。
   update-index の非 0 は新しい原因 `INDEX_NORMALIZE_FAILED`(exit 2・測定不能)。実 index は触らない。
2. `_selftest_body`: skip-worktree 腕(index= 不正 bytes・`S`・作業ツリー= 正しい bytes → 返った tree の blob= `hash-object` の値・実 index の `ls-files -s/-v` 不変)+対照腕(フラグなし)+assume-unchanged 腕を追加。
3. W1 の注記を「正規化を含む・C18(ECO-092)と同一」に改め、限界に sparse-checkout(sparse 外の path は index の内容のまま残る・index≠HEAD の稀な場合は検査していない bytes を束縛— ECO-092 r1 IA-03 の**訂正後**の文言)を追加。
4. **selftest の CI 結線(候補)**: `.github/workflows` に `python method/tools/bomdd-witness.py --selftest` を追加(worklist と同じ形)。採否は製造裁定(ハーネス `.github` の変更)。
5. 採らない: hook・receipt 形式・verify の判定規則の変更 / sparse-checkout 対応 / bomdd-run.py・bomdd-job.py の変更。

## 2. 影響なし予測(起票段階・反証可能)

起票の diff は台帳系のみ。製造時(候補): `bomdd-witness.py`(関数 1 本の正規化+selftest 腕+注記)・(4 を採る場合)`.github/workflows/*.yml` 1 行+台帳系。self-conformance の C1〜C18 判定不変(本ツールは C 検査の対象外)。
フラグ 0 件の作業木では receipt の tree は是正前後で同一(V2 で実測)。既存の witness(`.git/bomdd-witness/*.json`)は tree 一致なら ADVANCE のまま。

## 3. 受入条件(製造時の候補・二部形)

- V1(条件): selftest の追加腕(skip-worktree / 対照 / assume-unchanged)が PASS し、`--selftest` の 1 行目が `ADVANCE …` であること。
- V2(条件): フラグ 0 件の作業木で是正前(baseline のツール)と是正後の `worktree_tree` が同一 tree であること。
- V3(条件): 検査官の sparse-checkout 環境(S/h 多数)で、是正後の tree の blob が作業ツリーの bytes と一致し、是正前は index の bytes だったこと(自然発生環境での反転)。
- V4(条件): `update-index` の失敗が `INDEX_NORMALIZE_FAILED`(exit 2)で止まること(失敗注入)。
- V5(条件): diff 窓・self-conformance 全 PASS・CI success(4 を採る場合は CI で selftest が走ること)。
- V6(条件): 異系統の独立検査 ACCEPT(r1 境界探索 → r2 是正確認+回帰)。
- V7(条件): 較正 receipt(trigger ①③)。

## /preflight receipt(起動経路: **自発** — 既記録の欠陥の起票)

- 分類= 既知の欠陥の起票(ECO-092 §4 範囲外の発見・OBS-20261003-02 の同型)。baseline= ECO-095 クローズ commit `a2eae9e`(2026-10-04)= **confirmed** / 次番 096= **confirmed** / 機序= **confirmed**(L115〜150 実読・ECO-092 の再現と同じ経路)/
  selftest が CI・self-conformance に無い= **confirmed**(grep 0 件)/ 同一ファイルへの進行中 ECO= **confirmed**(なし)。
- 開始判定: **PROCEED**(起票まで)・製造は裁定待ち・override 0。

## /converge receipt(起動経路: 自発 — ECO-092 の設計の転用)

- **判定: 収束**(round 軌跡: 2→0)。
- DoD: ✔ ECO-092 と同じ正規化(2 呼び出し)/ ✔ 失敗は測定不能の原因語彙(本ツールの P5-06 の流儀)で止める / ✔ 対の腕を selftest に置く / ✔ sparse の限界は訂正後の文言 / ✔ selftest の結線の穴を宣言。
- round 1(新規 2 件): ①原因語彙は既存の `ADD_FAILED` / `WRITE_TREE_FAILED` に倣い `INDEX_NORMALIZE_FAILED` を足す(W6 の語彙表に追加)②selftest が CI に無い— 腕を足しても毎 push で走らない → 結線を候補 4 に(ハーネス変更なので製造裁定)。round 2: 0 件。
- 検証した主張: 機序(実読)/ selftest の結線なし(grep)/ ECO-092 の再現と修正(同セッション)。
- 敵対自問: 「bomdd-witness は受理側の運転層で、pre-push の遮断には関与しないので優先度は低いのでは」— 低いが、receipt が『検査済み』として束縛する bytes が検査対象と違う状態は ECO-092 と同じ偽証明で、標準の裁定(偽陰性は実害待ちにしない)の対象。起票して製造の時期は人が決める。
- 未収束事項: なし(候補 4 の採否は製造裁定)。

## 4. 製造(2026-10-04・製造者 EQ-001)

- **裁定(user 2026-10-04)**: 「A」= 製造と異系統の独立検査を今回行う。
- **製造裁定(producer・候補 4 の採否)**: 採用。理由= selftest は手動実行のみで、腕を足しても毎 push で走らなければ恒久較正にならない(ECO-039 以来の「陽性対照は常設」の原則)。
  worklist.py と同じ形で fast job に 1 行(ubuntu / windows の両 OS で走る)。ハーネス `.github` の変更は allowed_paths に宣言済み。
- 製造物: `method/tools/bomdd-witness.py`= `_normalize_index_flags(root, env, paths=None)`(一時 index 上で `ls-files -v -z` → S / 小文字タグ → `update-index --no-assume-unchanged` と `--no-skip-worktree` を別呼び出し・失敗は (False, 理由))/
  `worktree_tree` の結線(複製の直後・失敗は `INDEX_NORMALIZE_FAILED`〔git 起動不能は `GIT_UNAVAILABLE`〕・exit 2)/ `TREE_CAUSES` に語彙追加 / `TREE_DEFINITION`・W1 注記(正規化と sparse の限界= ECO-092 r1 IA-03 の訂正後の文言)/
  selftest に 4 腕(skip-worktree・assume-unchanged・対照・失敗〔index に無い path〕+語彙の存在)。`.github/workflows/self-conformance.yml`= fast job に `bomdd-witness.py --selftest` 1 行。
  hook・receipt 形式・verify 規則・bomdd-run/job は不変。

## 5. 受入の実測(2026-10-04・製造者・独立検査 r1 の前)

- **V1**= PASS(観測: `python method/tools/bomdd-witness.py --selftest` → `ADVANCE OK: selftest PASS(…)`・exit 0。**陽性対照**: `_normalize_index_flags` を no-op に差し替えた変異で `STOP SELFTEST_FAIL: 3 件`(kb-skip-worktree・kb-assume-unchanged・kb-normalize-fail)→ 復元で ADVANCE= 新しい腕が正規化の有無を弁別する)。
- **V2**= PASS(観測: 本リポの作業木〔S/h 0 件〕で是正前の経路〔複製+add -A〕と `worktree_tree` が同一 tree `06c689e49997…`・err None)。
- **V4**= PASS(観測: selftest の失敗腕= index に無い path を正規化対象に渡すと `update-index --no-assume-unchanged 失敗(exit 128・1 件)` を理由に (False, …)。本番経路では `INDEX_NORMALIZE_FAILED` に写像〔読解・`worktree_tree` の分岐〕)。
- **V3**(検査官の sparse-checkout 環境)・**V5**〜**V7**= 独立検査とクローズで。

## 6. 独立検査(異系統・Codex EQ-002・入口 bomdd-run から `--report`/`--range` つきで起動・workspace-write)

### 6.1 r1(2026-10-04・range= 境界探索)— 報告: [independent-inspection-eco-096.md](reports/independent-inspection-eco-096.md)

- 起動: 製造 commit `f34a6d6`(witness tree 21920a69e1b1・入口 `ADVANCE ECO-096 OK → next · launching`)→ `cell exit 0` → `report ACCEPT sha256:478a2d514135 (EQ-002)`。作業木 clean・commit 0・`.git/index` 操作 0・外部 API なし。
- 判定: **ACCEPT**(所見なし・blocking 0・non-blocking 0)。V1 PASS(selftest ADVANCE・no-op 変異で STOP 3 腕)/ V2 PASS(隔離リポ・フラグ 0 件で同一 tree)/ V3 PASS(検査官の自環境は今回 S/h **0 件**〔r2 の 1151 件とは sandbox 構成が異なる〕→ 隔離リポで代替・サブディレクトリ・空白・非 ASCII の 3 例で是正前= index・是正後= 作業ツリー)/
  V4 PASS(失敗注入で `UNMEASURABLE TREE_UNAVAILABLE(INDEX_NORMALIZE_FAILED)`・produce exit 2)/ V5 PASS(窓 5 パス・workflow 2 行・fast matrix のみ)。
  境界探索 20 行(assume-only・両フラグ・複数+サブディレクトリ・空白・非 ASCII・削除+S・未追跡・ignore・intent-to-add・staged 削除・produce→verify 往復と変更後の TREE_MISMATCH〔是正前は index 側に固定され変更を識別しない対照〕・2 オプション同時指定の独立再現〔逆順でも S が残る〕・原因語彙・CI 結線・副作用)で偽証明 0・実 index 変化 0。
- 検査官の計器所見(自己訂正): PowerShell の `-match` は大文字小文字を区別せず `H` 1161 件を誤算入 → `-cmatch` で 0 件に訂正(報告に明記)。
- 次: r2(range= 是正確認+回帰・是正なしのため回帰のみ: V1〜V5 の再測+境界表 6 行)— playbook §3 の規則どおり ACCEPT は是正確認+回帰の round で確定する。

## 7. クローズ(クローズ時に追記)
