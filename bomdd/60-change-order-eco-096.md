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

## 4. 製造・受入・クローズ(製造時に追記)

## 5. 裁定待ち

製造と異系統の独立検査(ECO-092 と同型・r1+r2)の着手時期(今回 / 別セッション)。
