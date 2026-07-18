# cli-cad-01 介入台帳(全交信記録 — transfer-test §5 様式)

## ハーネス記録(要求値と実到達値を分離)

| 役割 | provider / model(要求) | model(実到達) | クライアント/ハーネス | 隔離方法 |
|---|---|---|---|---|
| CAD 設計者=観測者(同一人格・交絡は §3 に記帳) | Anthropic / claude-fable-5 | claude-fable-5 | Claude Code(本セッション) | n/a |
| 独立検査官 | Anthropic / (セッション継承) | claude-fable-5(継承) | Claude Code Agent(general-purpose・fresh 文脈) | 隔離 dir+指示ベース遮断 |
| 製造工場 | OpenAI / (codex プラグイン既定) | **gpt-5.6-sol**(~/.codex/sessions 2026-07-18 rollout の model フィールド。サーバ側の最終確認は unknown) | Codex CLI(codex:codex-rescue 経由・task-mrpylsw5-b46bg8) | 隔離 dir+指示ベース遮断 |

隔離の限界(protocol §3): 検査官・工場とも物理遮断ではない(リポ・web への到達可能性は残る)。
指示+隔離 dir による遮断であり、「合格は弱く不合格は強い」片側検出器として扱う。

## 交信ログ

| # | 時刻(2026-07-18) | 方向 | 内容(要旨) | 分類 |
|---|---|---|---|---|
| 1 | kit 凍結後 | 観測者→検査官 | 検査官ブリーフ(役割・kit パス・規律 3 点・成果物・自己検証手順)。CAD 解釈の助言なし | work-order 発行(検査官) |
| 2 | oracle 凍結後 | 検査官→観測者 | 納品報告(91 検査・期待値導出表・U 回避一覧・自己検証結果) | 納品報告 |
| 3 | oracle 凍結後 | 観測者→工場(rescue 経由) | work-order.md への委譲文(kit パス+厳守事項の転記のみ。方法論・実装の説明なし) | work-order 発行(工場) |
| 4 | 製造中 | 観測者→rescue | 完了待ちと報告依頼(モデル実到達値・納品確認・仮定要約・質問の有無)。「質問には回答するな」を明示 | 手続き連絡(tooling) |

| 5 | 製造中 | rescue→観測者 | 「フォワーダ専任のためポーリング不可」— 状態監視は観測者側のファイルウォッチャで代替 | tooling_gap(1 件・工場非介入) |
| 6 | 納品後 | 観測者 | 納品検出(worklist.py+assumptions.md)→ 受入実施。工場からの質問・追加交信なし | 記録のみ |

## 最終集計

- method_explanation: **0 件**
- rescue(救済): **0 件**
- customer_ruling: **0 件**(工場からの契約質問自体が 0 — 未規定次元は assumptions.md 32 件へ自己記帳)
- tooling_gap: **1 件**(#5 — 監視経路の代替。工場の製造には非介入・成功帰属に影響なし)
