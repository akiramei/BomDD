# 導出の記録 — ECO-097 / ViewPrism2 ECO-145(統括 AI・2026-10-05)

事前登録 R1(M の行の分類)・R2(人へ戻した判断)と、導出の 1 件 1 行の記録。種別は導出時に付け、事後に付け替えない。

## 役割

- 裁定層(10・20・30・31)= 人が裁定済みの版(ViewPrism2 f622c3c・bom-v4.1 のまま・**本試行で不変**)
- 導出(32・33・テスト → ID の対応・表の仕様)= 統括 AI(BomDD producer EQ-001・claude-fable-5-1)
- 製造(trait の付与・cp_results の拡張)= 工場(Codex gpt-5.6-sol・[ブリーフ](factory-brief-eco-145.md))
- 導出の意味の審査= 異系統の検査官(EQ-002)

## R1 — M の `invariants` の分類(1 行 1 件)

| # | 単位 | 行 | 分類 | 裁定層の所在 | 処置 |
|---|---|---|---|---|---|
| 1 | M-THUMB-008 | INV-009 元画像へ書き込まない | 参照化 | 30 E-THUMB-020 invariants(同文) | 行を削除 |
| 2 | M-THUMB-008 | 読み取り不能キャッシュは削除して再生成 | 参照化 | 20-spec.md L346・REQ-106 rationale | 行を削除 |
| 3 | M-THUMB-008 | EXIF 適用は表示系のみ — pHash 入力には適用しない | 参照化 | 20-spec.md L352・REQ-085 statement | 行を削除 |
| 4 | M-DB-007 | 接続は単一共有+SemaphoreSlim シリアル化(K-SQLITE) | 製造手段 | 決定は 31 K-SQLITE(ADR-0003) | `manufacturing_decisions` へ(K の参照として) |
| 5 | M-DB-007 | migrations テーブル契約は REQ-004 のとおり | 参照化 | REQ-004 | 行を削除 |
| 6 | M-DB-007 | (ECO-059)スキャンバッチの失敗は全ロールバック | 参照化 | 30 E-DB-010 invariants(同旨) | 行を削除 |

**参照化 5・製造手段 1・人へ戻す 0・分類不能 0**。対象 2 単位で「M が自分の言葉で持つ設計の内容」= 0 行(R1 成立)。
ECO-090 の `baseline-count.py` の再実行は受理後に追記する。

起票時の仮の分類との差: #2・#3 は「人へ戻す」→「参照化」(事前登録の変更の履歴・製品側の着手前に訂正)。原因= E-BOM(30)だけを読んで裁定層に無いと断定した。

## R2 — 人へ戻した判断(1 件 1 行)

| # | 判断 | 種別 | 結果 |
|---|---|---|---|
| 1 | REQ-106 の statement と rationale の食い違い(rationale の受入記載は「キャッシュファイル破損 → 削除+再生成」を REQ-106 の受入に挙げるが、statement はそれを述べない)。検査官 r1 IA-01 が発端 | **導出不能**(裁定層の文の中の食い違い・どちらが正かは裁定層からは決まらない) | 製品側 gate 2 で人へ戻す(受入の提示に含める)。それまでは statement に合わせて trait を外した(検査は REQ-040 の検査として残る) |

**1 件**(導出時は 0 件・検査官の審査の後に 1 件)。機械的派生 0。導出で**人へ戻さなかった**判断(統括 AI が決めたもの・列挙):

1. M の `invariants` を空にするとき、欄ごと消してコメントで理由を残す(ID だけの行を残さない)。
2. 欄名 `manufacturing_decisions`・`when`・`on_fail` と、その語(acceptance / product-fix / instrument-recovery / human-approval)。
3. CP-DB-006 の `requirement_refs` に REQ-010 を入れ、REQ-005 を入れない(行のテストが実際に検査する内容に合わせた。E-DB-010 の requirement_refs とは一致しない)。
4. CP-THUMB-007 の `invariant_refs` に INV-009 を入れる(E-THUMB-020 が負う不変条件。対象行に検査するテストは無い= 表に「検査なし」と出る)。
5. テスト → REQ の対応 26 本(24 本に REQ・2 本は「なし」)。**検査官の審査で 2 本を是正**: 破損キャッシュのテストから REQ-106 を外す(誤り 1)・COLLATE のテストに REQ-010 / REQ-014 を付ける(漏れ 1)= 最終 25 本に REQ・1 本は「なし」。この 2 件は「導出の欠陥」(統括 AI の対応の誤り)として数える。
6. REQ を特定できない 2 本(解像度取得・COLLATE NOCASE)に、無理に近い REQ を当てない。
7. trait の名前(`req` / `inv`)と、付ける位置(メソッド)。
8. 表の区分の定義を CP 行と同じにし、「人の承認で検査」は参照する行がすべて depth G のときだけにする。
9. ECO-144 が vector の文言に書いた【REQ・落ちたら…】を消さない。

これらが後で「人が決めるべきだった」と判定されたら、R2 の機械的派生ではなく「導出の欠陥」として記録する(事前登録の読み方)。
3 と 6 は、裁定層の側の空白(REQ-005 を検査するテストが対象行に無い / EXIF なしの寸法取得と COLLATE を述べる REQ が無い)を**表に見せる**判断で、空白を埋める判断ではない。

## 導出(1 件 1 行)

| # | 入力(裁定層) | 導出先 | 内容 |
|---|---|---|---|
| D1 | E-THUMB-020(invariants・REQ-040/085/104〜106)・20-spec §2.5 | 32 M-THUMB-008 | invariants 3 行を削除・コメント 1 行 |
| D2 | E-DB-010・REQ-004・K-SQLITE | 32 M-DB-007 | invariants 3 行を削除・manufacturing_decisions 1 行 |
| D3 | REQ-040/085/104/105/106・INV-009 | 33 CP-THUMB-007 | requirement_refs・invariant_refs・when・on_fail |
| D4 | REQ-003/004/010/028 | 33 CP-DB-006 | requirement_refs・when・on_fail |
| D5 | D3・D4 | テスト 4 ファイル | メソッドに trait `req`(工場) |
| D6 | D3・D4 | bomdd/cp_results.py | 裁定層の ID ごとの表(工場) |
| D7 | D6 | .claude/skills/eco-fix 手順 3.1 | 「ID ごとの表も添える」の 1 文 |

## 導出中の発見(記録のみ)

- **裁定層が M の ID を本文で名指す**: 20-spec.md L1345・30-ebom.yaml L379「単一共有接続 M-DB-007」。R5(a)(E → M の参照 0 件)は**参照の欄では 0・本文では 2**。直すと裁定層の文の変更になるため触らない。
- **M の `interface_contract` に混ざる裁定層の内容**(件数の記録・事前登録「測らないこと」): M-THUMB-008= `cache_key`(MD5+`-v2`・仕様 L342〜344)・`params`(長辺 256 ほか・REQ-040)の 2 項目 / M-DB-007= `schema`(テーブル一覧・仕様 §2.0)の 1 項目。
- **裁定層の列挙に K-BOM が抜けていた**(BomDD ECO-097 §1.1 → §6 で補正)。
- **E-BOM の requirement_refs と、CP 行が実際に検査する REQ は一致しない**: E-DB-010 は REQ-005 を持つが CP-DB-006 のテストは検査しない / CP-DB-006 のテストは REQ-010(同期フォルダの一意性・連鎖削除)を検査するが E-DB-010 は持たない。
  ID ごとの表は CP 行の refs から作るため、REQ-005 は表に出ない(E 品目の requirement_refs から作れば「検査なし」と出る)。**表の ID の集合を CP 行の refs から取るか、E 品目の requirement_refs から取るか**は、反映の時の設計の入力。

## 導出の欠陥(検査官・独立レビューの後に判明・1 件 1 行)

| # | 欠陥 | 検出 | 処置 |
|---|---|---|---|
| X1 | 「破損キャッシュは削除して再生成する」に REQ-106 を当てた(ECO-144 の vector の【REQ-106】と REQ-106 の rationale を根拠にし、statement を読み比べなかった) | 検査官 r1 IA-01 | trait と 33 の vector を REQ-040 へ |
| X2 | 「COLLATE_NOCASE が主要列に付与されている」に REQ を当てなかった(REQ-010 の statement の「大文字小文字無視」・REQ-014 を引かなかった) | 検査官 r1 non-blocking | trait 2 つ・refs に REQ-014 |
| X3 | 表の ID の集合を CP 行の refs だけから取る仕様にした(AI が refs に入れなかった要求が表から消える= 統制 ① が自分の導出に依存する) | 統括 AI(製造後・表を見て) | 工場 r2: E 品目が負う ID も集合に入れる |
| X4 | 工場へのブリーフで「行は合格だが ID は測定不能」の腕を名指しで要求したが、納品物の合成データがそれを満たさないことを受理時に見逃した | 独立レビュー(変異の実行) | 工場 r3 で是正・受理側の変異で確認 |
