# 合同再独立検査結果(REV-01〜13 閉鎖判定)— ECO-016/017

> 検査官出力の原本転記(Codex・実応答モデル `gpt-5.6-sol`・セッション
> `019f9c8f-c6d5-7002-b20f-3a8e4f3797ac`)。read-only 実施・情報遮断(order 検証節・register
> verification 欄・前回報告の真正判定注記の読取り禁止)維持。最終 `git status --short` は空。
> 運用注記: 初回実行はランナー側 10 分タイムアウトで中断(中間所感のみ)— 同一スレッドを
> resume して完了(検査文脈は連続・fresh 性は初回起動時に確保)。

## 1. REV-01〜13 閉鎖判定表

| REV | 判定 | 再現条件・実測結果 | 該当行 |
|---|---|---|---|
| REV-01 | NEW | `git rm bomdd/hooks/pre-commit` で削除自身は起動せず、残る commit-msg モードも E08 未実行。同一 commit で `open_states: [applied]` にすると HEAD 側 closed ECO が open 扱いに。 | hooks/pre-commit:8–28、process-validator.py:127–153,373–397,529–552 |
| REV-02 | CLOSED | subject/中間 accept trailer/通常段落を再投入、`parse_trailers()` は `{}`。 | process-validator.py:297–325 |
| REV-03 | NEW | `--no-verify` で新規 ECO を直接 applied+同 commit で accept trailer にすると、`check_transitions()` を通らず linked evidence 採用。 | process-validator.py:329–369,400–433,554–572 |
| REV-04 | CLOSED | 重複 ID/非 mapping changes とも例外送出、再現なし。 | process-validator.py:185–216,500–505 |
| REV-05 | NEW | 非コメント 2 行 decoy+`exit 0` で IQ-02 `_hook_invokes_validator()` が true 通過。sandbox 名依存分岐も可能。 | process-qualification.py:95–106,138–152,386–395 |
| REV-06 | CLOSED | 初回 commit 失敗 mock 再演で exit 1、IQ-07 も HEAD 不在 FAIL。 | bomdd-init.py:357–385、process-qualification.py:177–182 |
| REV-07 | CLOSED | 空 hooks/ は fresh 分類、profile のみは SystemExit+復旧案内。 | bomdd-init.py:187–214,293–324 |
| REV-08 | CLOSED | 非 Git ルートは exit 2、証拠ゼロ縮約なし。 | process-validator.py:228–245,529–534 |
| REV-09 | CLOSED | mystery→rejected は E03 検出、旧状態検査が先行。 | process-validator.py:400–429 |
| REV-10 | CLOSED | HEAD 空+index 同時追加で E01 検出。 | process-validator.py:373–382,536–541 |
| REV-11 | CLOSED | `--runs 1/0` は argparse エラー、C11 判定・E04/E07 実 Git 負例組込済み。 | process-qualification.py:334–354,362–417、self-conformance.py:238–261 |
| REV-12 | NEW | `GIT_DIR` 等 routing 変数は除去確認も `GIT_TRACE` は残存し実 Git 子プロセスへ到達(外部ファイルへの side channel 余地)。 | process-qualification.py:62–79,222–233,374–379 |
| REV-13 | NEW | 通常 2-parent merge は閉鎖済みだが、`refs` は `"MERGE_HEAD"` を単一参照としてのみ扱い、octopus merge 第 3 親以降を反復しない。 | process-validator.py:262–294,500–505 |

## 2. 新規所見(7 件)

1. **NEW-ECO01617-01**(high)— enforcer hook 自身の削除・置換で E08 バイパス可能。
2. **NEW-ECO01617-02**(high)— index 側 profile で HEAD 側 closed ECO を open 扱いに再定義可能。
3. **NEW-ECO01617-03**(high)— validate が履歴上の違法 E02/E03 遷移(`check_transitions()` 省略)を再演しない。
4. **NEW-ECO01617-04**(medium)— IQ-02 は依然 token 存在検査のみ、制御経路の同一性未検証。
5. **NEW-ECO01617-05**(medium)— `GIT_*` 除去が denylist 限定、`GIT_TRACE` で side channel 残存。
6. **NEW-ECO01617-06**(medium, false-reject 方向)— octopus merge 親集合の非列挙。
7. **NEW-ECO01617-07**(medium)— `bomdd-init` の Git 操作が呼出元 `GIT_*` 環境を無加工継承(qualification 失敗前の外部副作用リスク)。

## 3. 総合判定

**REJECT**。原攻撃 13 件中 8 件は閉鎖、残る 5 件も原条件自体は改善済みだが、high 重大度の
バイパス 3 件(hook 自己削除・profile 自己再定義・履歴違法遷移の非検出)が残存しており
line-ready 未達。

---

実応答モデル: `gpt-5.6-sol`
セッション識別子: `019f9c8f-c6d5-7002-b20f-3a8e4f3797ac`

---

## 真正判定(当方検証・2026-07-26 — 検査官出力の後付け注記)

- 実プローブ 3 件(NEW-01/02/03 — fresh scaffold 上で再現条件を実行):
  - NEW-01: `git rm bomdd/hooks/pre-commit` → **commit 成立**(pre-commit 不在で E08/E01 検査自体が
    走らない・commit-msg モードは check_equipment を呼ばない)= CONFIRMED。
  - NEW-02: 同一 commit で profile の `open_states` を `[applied]` へ書換え+保護パス変更 →
    **commit 成立**(enforcement が index/worktree 側 profile を読むため、改竄 profile が自身の
    通過条件を定義できる)= CONFIRMED。
  - NEW-03: `--no-verify` で新規 ECO を born-applied+同 commit trailer → **validate OK**
    (linked evidence は「遷移の発生」のみ照合し合法性を照合しない)= CONFIRMED。
- コード読解 3 件: NEW-05(GIT_TRACE* が denylist 外 — 事実)・NEW-06(MERGE_HEAD 単一解決 —
  事実・false-reject 方向)・NEW-07(bomdd-init の git() は環境無加工 — 事実)= CONFIRMED。
- NEW-04 = **CONFIRMED(限定)**: IQ-02 単独では decoy で欺けるが、同一 qualification run の
  OQ が対象リポの実 hook を sandbox で実行するため、不活性 hook は N1 で検出される
  (防御の重複はある — IQ 単独の弱さとして成立)。
- **裁定: 7/7 CONFIRMED(うち 1 件限定つき)・誤検出 0・REJECT は妥当**。通算(初回 13+
  再検査 7)= 20 提起・20 CONFIRMED。
- 構造的観測: NEW-01/02 は「**強制層(hook/profile)は自分自身を守れない**」— worktree 実体に
  依存する enforcement の原理的限界。完全閉鎖には commit 経路外の検査面(CI/validate の履歴
  再演= NEW-03 是正)との二層化が必要。
- 処置: 是正 ECO の起票裁定待ち。
