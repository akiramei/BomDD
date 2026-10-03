# 導出の記録 — ECO-094 / ViewPrism2 ECO-144(統括 AI・2026-10-03)

事前登録 M1(人へ戻した判断)と、導出の 1 件 1 行の記録。種別は導出時に付け、事後に付け替えない。

## 役割

- 約束の確定= 人(maintainer)・gate① 裁定「1:A 2:OK」(ViewPrism2 `decide(eco-144)` 9f32ef4・tag bom-v4.1)
- 導出(M-BOM unit の対応・Control Plan 行)= 統括 AI(BomDD producer EQ-001・claude-fable-5-1)
- 検査の製造= 工場(Codex gpt-5.6-sol・ブリーフ= 本リポ scratchpad の brief-eco-144-factory.md の写しを本記録末尾に添付)
- 期待値の意味の審査= 人(trace.md の欄)

## M1 — 人へ戻した判断(1 件 1 行)

| # | 判断 | 種別 | 戻した理由 | 結果 |
|---|---|---|---|---|
| 1 | 約束 ① の文言(SkiaSharp を「交換できる」とするか「交換しない部品= 宣言された結合」とするか) | **新しい保守の約束** | 叩き台「交換できる」が現状の宣言(32 substitutable: false・契約層の識別子出現・20-spec §2.10 exact ピン)と食い違う。約束の内容は人が確定する(ECO-094 手順 1) | A(宣言された結合)・2026-10-03 |

機械的派生(戻すべきでなかった判断)= **0 件**。②③ の文言確認は「約束の確定」の一部で、戻した判断に数えない(導出不能でも新しい機能でもない)。

## 導出(1 件 1 行・承認済み E/S 版 bom-v4.1 → M / CP)

| # | 入力(REQ) | 導出先 | 内容 | 新規/既存 | 落ちたときの振り分け |
|---|---|---|---|---|---|
| D1 | REQ-104(宣言された結合) | M-THUMB-008(既存・対応変更なし) | E-THUMB-020 → M-THUMB-008 の対応は既存(32 L137)。unit の新設なし | 既存 | — |
| D2 | REQ-104 | CP-THUMB-007 vector「版の一致」 | Infrastructure csproj・32 procurement・53 external_deps の SkiaSharp 版が同一文字列で exact | **新規 vector 1 本+テスト 1 本(工場)** | 不一致= 製品修正(台帳と実体のどちらが正かは 53 DEG 手順)/ ファイルが読めない= 測定系復旧 |
| D3 | REQ-104 | 53 SB-THUMB-020 `replacement_policy: declared-coupling`・K-SKIA watched_externals(既存) | 更新の経路= DEG → reinspect_on_change+affected_parts の再検査(CP-DUPQUALITY-030 全 fixture を含む・既存の known_traps) | 既存(参照の追加のみ) | 人の承認で検査(depth G・DEG 手順) |
| D4 | REQ-105(キャッシュ継続) | CP-THUMB-007 vector「キャッシュヒット」「キャッシュ世代移行 -v2」 | 既存 vector に REQ の対応と振り分けを付記 | 既存 | 製品修正 |
| D5 | REQ-106(壊れた画像での継続) | CP-THUMB-007 vector「壊れた jpg → null」「キャッシュ破損 → 削除+再生成」 | 既存 vector に REQ の対応と振り分けを付記 | 既存 | 製品修正 |
| D6 | REQ-104〜106 | 33 CP-THUMB-007 characteristic・tolerance・fixture・oracle | 約束 3 件を本行で検査する旨と、版の一致の exact 許容差を追記 | 既存行の改訂 | — |

導出で**人へ戻さなかった**判断(機械的派生として統括 AI が決めたもの・列挙): vector の文言 / 版の一致の検査方法(3 ファイルの文字列照合・exact の正規表現)/ テストの配置(CP-THUMB-007 の trait・新規ファイル)/ 振り分けの文言(製品修正・測定系復旧)/ 53 の欄名(`service_requirement_refs`・`replacement_policy`・candidate)。
これらが後で「人が決めるべきだった」と判定されたら M1 の「機械的派生」ではなく「導出の欠陥」として記録する(事前登録の読み方)。

## 工場への入力(ブリーフの要点)

対象= テスト 1 本(`tests/ViewPrism2.Tests/CpThumb144VersionPinTests.cs`)・src 不変・入力= 33 の vector・REQ-104・既存テスト 2 本の様式のみ・41/42/ECO order は渡さない・自己受入= build 0/0+フィルタ実行全合格・ずる報告必須。
