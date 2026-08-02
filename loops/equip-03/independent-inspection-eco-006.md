# ECO-006 独立受入検査報告(Codex fresh・read-only・2026-08-02)

- 検査官: OpenAI Codex(model family GPT-5・resolved= unknown〔自己申告・推定補完なし〕)
- セッション: 019fc264-0fc8-7da3-9327-abe783edd6bc(rollout jsonl 保存済み)
- 対象: BomDD-Plm eco-006-input..8a874ea
- 以下、検査官の最終報告全文(無改変転記):

---
## 1. 所見リスト

所見は計5件です。内訳: high 0件、medium 4件、low 1件。

### ID: IA-ECO006-01

- 深刻度: **medium**
- 主張: `M-BUILD-CORE-010` と `M-BUILD-VIEWER-011` の `artifact.path` は生成物専用 unit として過剰に広く、著述されたビルド入力まで吸収する。したがって `unmapped_files=0 / real_under_files=111` は満たしても、catch-all 化を防げていない。
- 証拠:
  - 粒度原則は「独立に再製造・交換でき、単独で自己受入できる単位」: [32-mbom.yaml:7](C:/Users/akira/source/repos/BomDD-Plm/bomdd/32-mbom.yaml:7)
  - core unit は `packages/core/` 全体を宣言し、`src/` 以外をすべて所有する: [32-mbom.yaml:133](C:/Users/akira/source/repos/BomDD-Plm/bomdd/32-mbom.yaml:133)、[32-mbom.yaml:143](C:/Users/akira/source/repos/BomDD-Plm/bomdd/32-mbom.yaml:143)
  - viewer unit も `packages/viewer/` 全体を宣言する: [32-mbom.yaml:148](C:/Users/akira/source/repos/BomDD-Plm/bomdd/32-mbom.yaml:148)
  - 宣言された再製造手順は `tsc -b` だが、`package.json` と `tsconfig.json` はその入力であり生成物ではない: [package.json:13](C:/Users/akira/source/repos/BomDD-Plm/package.json:13)、[packages/core/tsconfig.json:2](C:/Users/akira/source/repos/BomDD-Plm/packages/core/tsconfig.json:2)、[packages/viewer/tsconfig.json:2](C:/Users/akira/source/repos/BomDD-Plm/packages/viewer/tsconfig.json:2)
  - 実行済み前方一致プローブ出力:

    ```json
    {
      "existing_mapped_assignment_changes": 0,
      "captured_authored_package_files": [
        {"file":"packages/core/package.json","before":null,"after":"M-BUILD-CORE-010"},
        {"file":"packages/core/tsconfig.json","before":null,"after":"M-BUILD-CORE-010"},
        {"file":"packages/viewer/package.json","before":null,"after":"M-BUILD-VIEWER-011"},
        {"file":"packages/viewer/tsconfig.json","before":null,"after":"M-BUILD-VIEWER-011"}
      ]
    }
    ```
- 再現手順:
  1. `eco-006-input` と HEAD の `32-mbom.yaml` を比較する。
  2. frozen scorer の最長前方一致規則を上記4ファイルへ適用する。
  3. 変更前は未写像、変更後は生成物 unit に帰属することを確認する。
  4. `tsc -b` がこれらの入力ファイルを再生成する手順ではないことを各 `tsconfig.json` と root build scriptから確認する。

### ID: IA-ECO006-02

- 深刻度: **medium**
- 主張: `M-SCHEMA-013` は供与入力である ref-v0 スナップショットと、製造出力である PLM 出力契約スキーマを一つにまとめており、M-BOM 冒頭の粒度原則に適合しない。
- 証拠:
  - unit は `schemas/` 全体を所有し、ref-v0 と `plm-*` の両方を列挙する: [32-mbom.yaml:174](C:/Users/akira/source/repos/BomDD-Plm/bomdd/32-mbom.yaml:174)、[32-mbom.yaml:179](C:/Users/akira/source/repos/BomDD-Plm/bomdd/32-mbom.yaml:179)
  - 影響分析自身が、出力契約スキーマは意味的に `M-CORE-OUTPUT-004` の成果物だと認めている: [61-impact-analysis-eco-006.md:94](C:/Users/akira/source/repos/BomDD-Plm/bomdd/61-impact-analysis-eco-006.md:94)
  - routing では ref-v0 は工場へ供与される入力: [34-routing.yaml:9](C:/Users/akira/source/repos/BomDD-Plm/bomdd/34-routing.yaml:9)
  - 一方、出力契約スキーマは `M-CORE-OUTPUT-004` の製造対象: [34-routing.yaml:16](C:/Users/akira/source/repos/BomDD-Plm/bomdd/34-routing.yaml:16)、[40-work-order.md:31](C:/Users/akira/source/repos/BomDD-Plm/bomdd/40-work-order.md:31)
  - 実行済み写像プローブでは、来歴が異なる6ファイルすべてが `M-SCHEMA-013` に集約された。
- 再現手順:
  1. `schemas/ref-v0/*` と `schemas/plm-*.schema.json` を列挙する。
  2. `34-routing.yaml` と `40-work-order.md` で前者が入力、後者が製造出力であることを突合する。
  3. `artifact.path: schemas/` の前方一致により両集合が同一 unit に帰属することを確認する。

### ID: IA-ECO006-03

- 深刻度: **medium**
- 主張: 新 unit の `depends_on` は、変更内で採用した「由来・鋳造元」または実行依存のどちらとして読んでも不完全であり、その意味論自体も未裁定のままである。
- 証拠:
  - `M-BUILD-VIEWER-011` の依存先は viewer の2 source unitだけ: [32-mbom.yaml:152](C:/Users/akira/source/repos/BomDD-Plm/bomdd/32-mbom.yaml:152)
  - 実際の viewer build は core projectを明示参照する: [packages/viewer/tsconfig.json:7](C:/Users/akira/source/repos/BomDD-Plm/packages/viewer/tsconfig.json:7)
  - viewer packageも `@bomdd/core` に依存する: [packages/viewer/package.json:11](C:/Users/akira/source/repos/BomDD-Plm/packages/viewer/package.json:11)
  - `M-CI-012` は harness/oracle/CLIを依存先に持つが、同じworkflowが直接実行する build unitを含まない: [32-mbom.yaml:165](C:/Users/akira/source/repos/BomDD-Plm/bomdd/32-mbom.yaml:165)、[ci.yml:35](C:/Users/akira/source/repos/BomDD-Plm/.github/workflows/ci.yml:35)
  - cheat-log は `depends_on` の意味が「実行時依存」か「由来・鋳造元」か ref-v0 に規定されず、設計者裁定が必要だと明記する: [51-cheat-log.md:60](C:/Users/akira/source/repos/BomDD-Plm/bomdd/51-cheat-log.md:60)、[51-cheat-log.md:69](C:/Users/akira/source/repos/BomDD-Plm/bomdd/51-cheat-log.md:69)
- 再現手順:
  1. `M-BUILD-VIEWER-011` の `depends_on` と `packages/viewer/tsconfig.json` の `references` を比較する。
  2. `M-CI-012.depends_on` と `.github/workflows/ci.yml` の直接実行ステップを比較する。
  3. `51-cheat-log.md` の未裁定記録を確認する。

### ID: IA-ECO006-04

- 深刻度: **low**
- 主張: `oracle/` を `M-HARNESS-008` に併合しない結論自体には合理性があるが、根拠中の「test/ は工場へ渡る」という事実記述は routing と一致しない。
- 証拠:
  - M-BOM と影響分析は「oracle は非開示、test/ は工場へ渡る」と主張する: [32-mbom.yaml:130](C:/Users/akira/source/repos/BomDD-Plm/bomdd/32-mbom.yaml:130)、[61-impact-analysis-eco-006.md:78](C:/Users/akira/source/repos/BomDD-Plm/bomdd/61-impact-analysis-eco-006.md:78)
  - `factory_isolation` が明記するのは oracle 非開示と、工場へ供与する製造パッケージであり、既存 `test/` の供与ではない: [34-routing.yaml:9](C:/Users/akira/source/repos/BomDD-Plm/bomdd/34-routing.yaml:9)
  - work order は入力を「これがすべて」と限定し、テストfixtureは工場が自作すると定める: [40-work-order.md:16](C:/Users/akira/source/repos/BomDD-Plm/bomdd/40-work-order.md:16)、[40-work-order.md:22](C:/Users/akira/source/repos/BomDD-Plm/bomdd/40-work-order.md:22)
  - `test/` は供与入力ではなく製造対象として列挙される: [40-work-order.md:35](C:/Users/akira/source/repos/BomDD-Plm/bomdd/40-work-order.md:35)
- 再現手順:
  1. `34-routing.yaml:factory_isolation` の供与物を列挙する。
  2. `40-work-order.md` の全入力と製造対象を比較する。
  3. `test/` が既存供与物ではなく工場製造成果であることを確認する。

### ID: IA-ECO006-05

- 深刻度: **medium**
- 主張: §5 の「実リポ・全再実測」は最終コミット `8a874ea` の状態を一貫して表しておらず、工場3ファイル段階と最終5ファイル段階の証拠が混在している。
- 証拠:
  - §5 は lint infoを180、新 unit由来のR-005を4件と記録し、`git status` は3ファイルとする: [60-change-order-eco-006.md:75](C:/Users/akira/source/repos/BomDD-Plm/bomdd/60-change-order-eco-006.md:75)、[60-change-order-eco-006.md:81](C:/Users/akira/source/repos/BomDD-Plm/bomdd/60-change-order-eco-006.md:81)
  - 最終差分は5ファイル:

    ```text
     bomdd/32-mbom.yaml                  |  82 +++++++++++++
     bomdd/51-cheat-log.md               |  44 +++++++
     bomdd/60-change-order-eco-006.md    |  23 +++-
     bomdd/60-change-register.yaml       |   9 +-
     bomdd/61-impact-analysis-eco-006.md | 225 ++++++++++++++++++++++++++++++++++++
     5 files changed, 379 insertions(+), 4 deletions(-)
    ```

  - 最終 register は新5 unitを `affected_refs` から参照する: [60-change-register.yaml:112](C:/Users/akira/source/repos/BomDD-Plm/bomdd/60-change-register.yaml:112)
  - 最終個体への書込みなし lint API 再測定結果:

    ```json
    {
      "counts": {"error":0,"warn":0,"info":176},
      "r005":176,
      "r051":0,
      "r052":0,
      "newUnitFindings":[]
    }
    ```

  - ViewPrism2回帰は対象revisionが§5に記録されていない。現在の `ViewPrism2` HEAD `6fe3706` の workspace再測定は `error 0 / warn 15 / info 502` で、記録された `0 / 12 / 502` を再現しなかった。revision不明のため、旧測定値が虚偽とは断定せず、再現不能な証拠と判定する。
- 再現手順:
  1. `git diff --stat eco-006-input..8a874ea` を実行し、5ファイルを確認する。
  2. 最終 registerを含めて pure `runLint(... eco:true ...)` を実行する。
  3. info 176・新 unit所見0を§5の180・4件と比較する。
  4. ViewPrism2について、§5に対象revisionと実行コマンドがないことを確認する。

## 2. 総合判定

**REJECT**

理由は、凍結された数値条件そのものは次のとおり独立再現できた一方、所有宣言の意味的品質に medium 所見が残るためです。

- 変更前: `unmapped_files=76`、`mapped_under_files=35`、`real_under_files=111`
- 変更後: `unmapped_files=0`、`mapped_under_files=111`、`real_under_files=111`
- 既存8 unitの既写像ファイルについて帰属変更: 0件
- 最終 lint: error 0 / warn 0、R-051 0、R-052 0
- `git diff eco-006-input..8a874ea --stat`: 変更5ファイルすべて `bomdd/` 配下

しかし、V1の数値は過広なpath宣言、異なる来歴の一括所有、欠落した依存関係を検出しません。特に IA-ECO006-01〜03 は、ECO-006が解消しようとする「正しい所有写像」の中心部分に関わるため、数値PASSだけで受入にはできません。

書込みを必要とする build/test/oracle 回帰は read-only環境で `mkdtemp ... EPERM` となったため、製品FAILではなく**独立再測定不能**と分類しました。判定理由には用いていません。

## 3. 検査モデル識別子の自己申告

- provider / client: OpenAI Codex
- model family: GPT-5
- exact resolved model identifier: **unknown**（このセッションから確認可能な識別子が公開されていないため、推定では補完しない）
