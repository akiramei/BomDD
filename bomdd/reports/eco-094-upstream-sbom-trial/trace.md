# 追跡表 — ECO-094 / ViewPrism2 ECO-144(M2: 承認済み REQ → E → M → CP → テスト → 実行証拠)

- 対象 revision: ViewPrism2 承認済み E/S 版= tag `bom-v4.1`(decide 9f32ef4)/ 導出と検査= fix commit(§実行証拠の欄に記す)。
- 読み方(事前登録): 各辺は参照元ファイル:行と参照先 ID。5 辺が揃えば「到達」。**到達= 正しい ではない** — 期待値の意味(約束を検査しているか)は人の審査欄(合 / 否 / 条件付き)。

## 構造(到達性)— 機械

| REQ | → E(30-ebom) | → M(32-mbom) | → CP(33)vector | → テスト(trait cp=CP-THUMB-007) | → 実行証拠(cp_results の行・実行の素性) |
|---|---|---|---|---|---|
| REQ-104 宣言された結合 | E-THUMB-020 `requirement_refs`(30 L409)・invariants(L417) | M-THUMB-008 `ebom_refs: [E-THUMB-020]`(32 L138)・`acceptance_refs: [CP-THUMB-007]`(L153) | CP-THUMB-007 vector「(ECO-144/REQ-104)版の一致」 | `CpThumb144VersionPinTests`(3 Fact: 抽出できる / 一致する / exact である・工場製造) | cp-results.xml sha256 793554f877aa(R8 是正後の再実行・是正前は 7533cb8e40cb で同値)・素性 Debug・2026-10-03T19:44:54+09:00・総数 977(合格 977)・**CP-THUMB-007= 合格(18 テスト)**・区分: 違反 0 / 測定不能 0 / 検査なし 4 / 人の承認 3 / 合格 57 |
| REQ-105 キャッシュ継続・世代移行 | 同上(L409・invariants L416) | 同上 | vector「キャッシュヒット」「(ECO-049)キャッシュ世代移行」 | `CpThumb007Tests.キャッシュヒットで再生成しない`・`CpThumb049ExifTests.キャッシュ世代移行_旧世代ファイルは参照されず新世代で正立生成され…` | 同上(同じ行・同じ実行) |
| REQ-106 壊れた画像での継続 | 同上(L409・invariants L415) | 同上 | vector「壊れた jpg → null」「キャッシュファイル破損 → 削除+再生成」 | `CpThumb007Tests.壊れたJpgはNullでキャッシュ記録なし_FMEA012`・`破損キャッシュは削除して再生成する` | 同上 |

S-BOM(53)側の結線: SB-THUMB-020 `service_requirement_refs: [REQ-104, REQ-105, REQ-106]`・`replacement_policy: declared-coupling`・`reinspect_on_change: CP-THUMB-007`・watched_externals K-SKIA(affected_parts に E-THUMB-020)。

**到達性= 5/5**(REQ → E → M → CP → テスト → 実行証拠の全辺が実在)。

欠けた辺・欄の不足(「欄が無い」と「書かれていない」を分ける):
- 欄が無い: **CP 行 → vector → テスト** の対応は文言(vector の末尾の【REQ-…】と trait cp)でしか結べない — 33 に vector の ID が無く、テストの trait は行(CP)単位。実行証拠も行単位(cp_results)。
  REQ ごとの到達は「同じ行の中の vector」を人が読んで辿る(機械では行までしか辿れない)— rehearsal.md の M3 と同じ粒度の限界。
- 欄が無い: 53 に上流の約束への参照欄が無かった(本 ECO で `service_requirement_refs` を candidate として追加)。10 に保守性要求の種別が無かった(`classification_hint: maintainability` を新設・validate_bom は意味検査しない)。
- 書かれていない: 32 の M-THUMB-008 には REQ の参照欄があるか未確認(E 経由で辿れるため本試行では足していない)。

## 意味(期待値の妥当性)— 人の審査(maintainer・accept 時)

| REQ | 検査する vector | 約束を検査しているか(合 / 否 / 条件付き) | 所見 |
|---|---|---|---|
| REQ-104 | 版の一致(3 ファイル同一・exact) | **条件付き**(maintainer 2026-10-03・gate②) | 「交換しない」という約束のうち検査できるのは「台帳と実体の版が一致し exact であること」まで。更新時の再検査経路(DEG 手順)は人の承認で検査(depth G) |
| REQ-105 | キャッシュヒット・世代移行 | **合**(同上) | |
| REQ-106 | 壊れた jpg → null・破損キャッシュ再生成 | **合**(同上) | |

意味審査の記入= maintainer の返答「A 104:条件付き 105:合 106:合」(ViewPrism2 ECO-144 gate②・golden n/a 受理と同時)。**M2'= 合 2・条件付き 1・否 0**。条件付きの内容= 約束 ① の「更新時の再検査経路」は機械の検査行に落ちず、人の承認で検査する部分が残る(導出の欠陥ではなく、約束の一部が depth G にしか置けないという限界— 事前登録の読み方どおり「導出の欠陥」には数えない)。

## M4 — 参照方向(対象機能)

- E → M の参照: 30-ebom の E-THUMB-020 ブロック(L405〜418)に `M-` の参照 **0 件** / 10-requirements の REQ-104〜106 に `M-` の参照 **0 件**(2026-10-03・fix 時点の grep で再測・同値)。**M4= 0 件(成立)**。
- CP/M → E: M-THUMB-008 `ebom_refs: [E-THUMB-020]`・CP-THUMB-007 は E-THUMB-020 `acceptance_refs` から参照される(向き= 下流 → 上流)。
