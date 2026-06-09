# BomDD フェーズ実行プロンプト集

[bomdd-playbook-v1.md](../bomdd-playbook-v1.md) の各フェーズを Claude Code(または任意の AI アシスタント)で実行するための指示書。各ファイルをそのままセッションに貼る/読ませることで、設計者 AI がそのフェーズの手順と規律に従う。

| ファイル | フェーズ | ゲート |
|---|---|---|
| [phase0-charter.md](phase0-charter.md) | チャーター(工場構成・予算・役割の固定) | G0 固定項目完備 |
| [phase1-brainstorm.md](phase1-brainstorm.md) | ブレスト→要求台帳 | G1 根拠精度 |
| [phase2-spec.md](phase2-spec.md) | 仕様化 | G2 マルチリーダー監査 / G2' 測定可能性 |
| [phase3-design.md](phase3-design.md) | BOM・工程設計 | G3 ドライラン |
| [phase4-manufacture.md](phase4-manufacture.md) | 製造(隔離ファクトリ) | 自己受入+ずる報告 |
| [phase5-accept.md](phase5-accept.md) | 受入・収束 | 未観測差分ゼロ+blocker ずるゼロ |

**正典はこの prompts/ である**(運用方針 2026-06-10)。Claude Code の slash command / skill 化は、forward-01 ループで playbook の有効性を検証してから、必要なら **adapter 層**として別途追加する。それまではリポジトリに `.claude/skills` を置かない(各ファイルに frontmatter を付けて `.claude/skills/<name>/SKILL.md` に置けばスキルになる、という変換は機械的に可能)。
