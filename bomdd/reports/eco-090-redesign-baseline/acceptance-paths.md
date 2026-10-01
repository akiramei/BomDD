# ECO-090 — 主 2 本の製品で受入を実際に決めているもの(2026-10-01・読み取りのみ)

調査= 製品リポごとに読み取り専用の調査エージェント(Explore)1 体ずつ。要の主張は製造者(claude)が自分で裏取りした(下の「裏取り」)。
どちらのリポも変更していない。主 2 本= ViewPrism2・ViewTube(一般的なアプリに近い — user の位置づけ 2026-10-01)。

## 結論

- **2 本とも、受入を決めているのは人の承認**(ViewTube= 利用者、ViewPrism2= 保守者)。CI はどちらにも無い。
  コミット時のフックが見るのは記録の形式(台帳・trailer・承認欄)で、テストの結果は見ない。
- **Control Plan は受入の入力でなく出力として使われる**: 2 本とも受入の手順(eco-accept)が、学んだ観点を CP の行へ書き足す。
  判定の時に CP の行を読む仕組みは無い。承認の根拠に挙がるのはテストの件数(「974/974」など)と AI の検査の記録で、CP の行ごとの結果は挙がらない。
- **結線の費用は 2 本で大きく違う**: ViewPrism2 はテストが CP の ID(trait)を持ち(65 行中 57 行)、集計だけで行ごとの結果が出る。
  ViewTube は受入テスト 836 件に CP の ID が 0 件、CP が参照する証跡ファイル 39 件は一度も作られていない。

## ViewTube

| 仕組み | 自動/手動 | 止める条件 | CP を読むか |
|---|---|---|---|
| pre-commit hook | 自動 | 検証器・UI 製造の検査ほか(`dotnet test` は走らない) | 読まない |
| validate_process.py(applied への遷移) | hook 経由 | red probe・独立レビュー完了・利用者承認欄・trailer・証跡ファイルの存在 | 読まない |
| 監督つき受入実行 | 手動(エージェント) | `$pass` と封印 | ハッシュを取るだけ(`validate_acceptance_disposition.py:911`) |
| release_gate.py | 手動 | hold point・利用者承認・件数 | 読まない |
| 工程表の quality_gate / hold point | 文書のみ | — | — |

- **常に赤を返す計器を読み替えて受け入れている**: 直近の受入で、監督つき実行は「合格なし(`pass false`)・終了コード 9」を返し、
  エージェントが件数を読み、利用者の言葉で受け入れている(ECO-VT-204・203。218 は監督の上限で打ち切り → 利用者が条件付きで承認)。原因は未確認。
- CP の不合格の基準(`stop_condition`)は「観測できなかった」を不合格に含める — 測定不能と違反を区別しない(ECO-089 で bomdd-lint について扱った混在と同型)。

## ViewPrism2

| 仕組み | 自動/手動 | 止める条件 | CP を読むか |
|---|---|---|---|
| pre-commit: validate_bom.py | 自動(bomdd/ 変更時) | 参照・状態・golden 語彙・lifecycle trailer | 構文のみ(`MAIN_LOADED` に含まれない) |
| pre-commit: bomdd-lint | 自動(隣接リポがあれば) | error 所見 | 参照の整合のみ |
| 機械受入 4 点(build / Tests / Oracle / validate) | 手動(AI が手順書どおり) | AI が緑でなければ止まる | 読まない(CP でのフィルタなし) |
| gate② golden / 保守者の受入 | 手動(人) | **出荷を決める** | 読まない |
| 工程表のガード(gate_g3_dryrun 等) | 文書のみ | — | — |

- テストの trait は 59 種で CP の 57 行に対応。trait の無い行 8(retired 1・depth G 3・unit 3・unit+G 1)・行の無い ID 2(CP-VIEWER-DIMCACHE・CP-VIEWER-IMPROVE)。

## 裏取り(製造者が自分で確認したもの)

- ViewTube: `bomdd/process/change-register.yaml:36780-36786`(pass false・終了コード 9 での受入)・`:38685-38690`(打ち切り後の条件付き受入)を実読。
  CP 証跡ファイル(`bomdd/plm-intake/sync-results/CP-*.json`)は作業木に無く、git の全履歴でも追加されたことが無い(`git log --all -- 'bomdd/plm-intake/sync-results/CP-*'` が空)。
  `33-control-plan` を読むコードの grep(validate_acceptance_disposition.py:911 はハッシュのみ・validate_phase3.py は hook/手順から呼ばれない)。
- ViewPrism2: `bomdd/validate_bom.py:137` の `MAIN_LOADED` に 33 が無いことを実読。trait の集計(57/65・行の無い ID 2)を自分のスクリプトで再計数して一致。

## 未確認

- ViewTube の「終了コード 9 / pass false」の原因(MTP のランナーの終了コードの可能性 — 未検証)。
- 各コミットの時点で hook が効いていたか(確認できたのはこの clone の設定だけ)。
- 報告されたテストの件数が実際の実行と一致するか(ViewPrism2 はテスト結果がコミットに結びついていない — ECO-143 以後は表に実行の素性が出る)。
