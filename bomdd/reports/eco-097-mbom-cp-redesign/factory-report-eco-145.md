[INFORM / COMPLETE]

DONE

- HEAD: `9f239a83ff48f5412b8a7d626661beafc119d9fd`
- 製造物: `bomdd/cp_results.py`（415行）・テスト4ファイル（付けた trait の数: 28）
- 自己受入: selftest OK / build 0 warning・13 errors（sandbox が NuGet `api.nuget.org:443` を拒否、NU1301）/ filter test 走らず（同じ NuGet 復元拒否）
- git status --short:
  ```
   M .claude/skills/eco-fix/SKILL.md
   M bomdd/32-mbom.yaml
   M bomdd/33-control-plan.yaml
   M bomdd/cp_results.py
   M tests/ViewPrism2.Tests/CpDb006Tests.cs
   M tests/ViewPrism2.Tests/CpThumb007Tests.cs
   M tests/ViewPrism2.Tests/CpThumb049ExifTests.cs
   M tests/ViewPrism2.Tests/CpThumb144VersionPinTests.cs
  ```
- 読んだファイル一覧: `bomdd/cp_results.py`、`bomdd/33-control-plan.yaml` の CP-THUMB-007・CP-DB-006 行、指定されたテスト4ファイル
- ずる報告:
  - 関数分割として `classify_ruled` を追加した。
  - `load_run` の3要素戻り値を維持するため、既存辞書を継承した `CpResults` の `ruled` 属性に req/inv 結果を載せた。
  - `ruled_orphans` は `id`・`tests`・`fail` を持つ dict のリストとした。
  - 複数の参照CP行は33での出現順を維持し、Markdownではカンマ区切りとした。
  - refsリスト内の空文字・文字列以外はIDとして扱わないこととした。
- commit: していない。