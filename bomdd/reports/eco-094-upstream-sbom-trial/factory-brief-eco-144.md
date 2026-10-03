# 製造ブリーフ — ViewPrism2 ECO-144(検査 1 本の製造・工場= Codex)

- 役割: **producer(工場)**。対象リポ: C:\Users\akira\source\repos\ViewPrism2(作業ディレクトリ= リポのルート・HEAD は `git rev-parse HEAD` で確認して報告に写す)。
- 製造対象: **テスト 1 本だけ**(`tests/ViewPrism2.Tests/CpThumb144VersionPinTests.cs`・新規)。**src は変更しない。他のテスト・bomdd/ 配下・csproj も変更しない。commit しない。**
- 入力(これがすべて。これ以外を参照しない): 本ブリーフ / `bomdd/33-control-plan.yaml` の CP-THUMB-007 の最後の vector「(ECO-144/REQ-104)版の一致」/ `bomdd/10-requirements.yaml` の REQ-104 /
  既存テストの様式= `tests/ViewPrism2.Tests/CpThumb007Tests.cs`(trait の付け方・名前付け)と `tests/ViewPrism2.Tests/CpAxamlLintScrollViewerPaddingTests.cs`(リポのルートの解決= `ViewPrism2.sln` を上へ探す `RepoRoot()`)。
- 読まないもの: `bomdd/41-fixed-oracle.yaml`・`bomdd/42-*`・`bomdd/60-change-order-*.md`・`.claude/`・`AGENTS.md`・`CLAUDE.md`。

## 検査の仕様(CP-THUMB-007 vector・REQ-104)

クラス: `[Trait("cp", "CP-THUMB-007")] public sealed class CpThumb144VersionPinTests`(xunit.v3・`[Fact]`・日本語メソッド名は既存流儀に合わせてよい)。

1. **版の一致**: 次の 3 箇所の SkiaSharp の版文字列を実ファイルから読み、**3 つが同一**であることを `Assert.Equal` で検査する(期待値のリテラル `3.119.4` を**テストに書かない** — 台帳と実装の一致を測る検査であり、版そのものを固定する検査ではない):
   - `src/ViewPrism2.Infrastructure/ViewPrism2.Infrastructure.csproj` の `<PackageReference Include="SkiaSharp" Version="…" />`(正規表現で抽出)
   - `bomdd/32-mbom.yaml` の procurement 行 `{ package: SkiaSharp, version: …, … }`(行内の `package: SkiaSharp` の後の `version:` の値を正規表現で抽出。YAML パーサは使わない— 依存を増やさない)
   - `bomdd/53-service-bom.yaml` の `- id: SB-THUMB-020` ブロック内の `external_deps: [{ kbom_ref: K-SKIA, version: "…" }]`(正規表現で抽出)
2. **exact であること**: 3 つの文字列がすべて `^\d+\.\d+\.\d+$` に一致する(範囲指定・`*`・`[`・`(` を含まない)。
3. **測定系復旧の分離**: 3 ファイルのいずれかが読めない/抽出できないときは、`Assert.Equal` の不一致ではなく、**原因(どのファイル・何が抽出できなかったか)を含む失敗メッセージ**で落とす(`Assert.Fail($"…")`)。
   = 製品側の違反(版の不一致)と治具の不能(ファイル/パターン)を失敗メッセージで区別できるようにする。
4. リポのルートは `ViewPrism2.sln` を出力パスから上へ探す(既存の `RepoRoot()` と同じ手法。共有ヘルパへの切り出しはしない— 既存ファイルを変えない)。
5. 1 クラス・`[Fact]` は 2〜3 本(一致 / exact / 抽出可能性)に分けてよい。各 Fact にも `[Trait("cp","CP-THUMB-007")]` が効くようクラスに付ける。

## 自己受入(製造完了の条件・結果を報告に写す)

- `dotnet build tests/ViewPrism2.Tests` が 0 error / 0 warning(TreatWarningsAsErrors の方針— warning も出さない)。
- `dotnet test tests/ViewPrism2.Tests --filter "FullyQualifiedName~CpThumb144VersionPinTests"` が全合格(**`-p:TestingPlatformCommandLineArguments` を渡さない**)。
  フィルタ付き実行は自己受入のみ。全件実行と cp_results は受理側が行う。
- `git status --short` が **`?? tests/ViewPrism2.Tests/CpThumb144VersionPinTests.cs` と、受理側が先に置いた ` M bomdd/33-control-plan.yaml`(導出・工場は触らない・戻さない)の 2 行だけ**。それ以外の変更が出たら戻す。

## ずる報告(cheat-log 形式・必ず書く)

BOM/REQ/本ブリーフから導けずに慣習で埋めた判断を**全件**列挙する(0 件なら「0 件」と書く)。例: 抽出の正規表現の形・メソッド名・失敗メッセージの文言。

## 報告(最終メッセージ全文・ハーネスが保存する。報告ファイルを自分で書かない)

```
[INFORM / COMPLETE]

DONE            ← または BLOCKED <理由>

- HEAD: <sha>
- 製造物: tests/ViewPrism2.Tests/CpThumb144VersionPinTests.cs(<行数>)
- 自己受入: build <0/0> / filter test <N/N>
- git status --short: …
- 読んだファイル一覧: …
- ずる報告: …
```
