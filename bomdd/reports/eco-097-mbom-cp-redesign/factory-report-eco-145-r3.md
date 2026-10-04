[INFORM / COMPLETE]

DONE

- HEAD: `9f239a83ff48f5412b8a7d626661beafc119d9fd`
- 製造物: `bomdd/cp_results.py`（632行）
- 自己受入: selftest OK / py_compile OK / F2 の変異 FAILED になった
- 所見ごとの処置:
  - F1: E-BOM 読取例外と ID 表生成全体を隔離。不正 UTF-8・非文字列 refs/ID・join を防御し、行ごとの表と終了コード 0 を維持。
  - F2: 合格行 CP-G に全件 Skip の ID を同居させ、行=合格・ID=測定不能を検査。
  - F3: invariant_refs、混在型 refs、main 配線、孤立 ID、全件 NotRun、`.get`、F1 の各異常入力を selftest に追加。
  - F4: refs がなくても孤立 ID の別欄を出力。
  - F5: `\bINV-[A-Z]*\d+\b` と境界ケースを実装・検査。
  - F6: refs と req/inv trait の前後空白を除去。
  - F7: `build(..., ebom_path=None)` と `--cp` 単独に専用理由を設定。通常の main は `DEFAULT_EBOM` を使用。
  - F8: `via_rows` を JSON に追加し、E 品目のみ由来の Markdown 表示を `E-A(CP-A 経由)` 形式に変更。
- git status --short:
  - ` M .claude/skills/eco-fix/SKILL.md`
  - ` M bomdd/32-mbom.yaml`
  - ` M bomdd/33-control-plan.yaml`
  - ` M bomdd/cp_results.py`
  - ` M tests/ViewPrism2.Tests/CpDb006Tests.cs`
  - ` M tests/ViewPrism2.Tests/CpThumb007Tests.cs`
  - ` M tests/ViewPrism2.Tests/CpThumb049ExifTests.cs`
  - ` M tests/ViewPrism2.Tests/CpThumb144VersionPinTests.cs`
- 読んだファイル一覧: `bomdd/cp_results.py`
- ずる報告: なし。既存の他7ファイルは変更せず、commit もしていない。F2 の一時変異は復元済み。禁止指定されたファイルは読んでいない。