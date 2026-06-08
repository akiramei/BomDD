# ① S-BOM ベースライン(稼働中構成)

製造済み MoviePad-BOM の稼働部品。**外部知識(K-BOM)依存**と**受入深さ**を記録し、劣化イベントに備える。

## K-BOM(参照される外部/設計知識)
| ID | 知識 | version |
|---|---|---|
| KB-CSHARP-IMMUTABLE | C# 不変 record/ドメイン慣習 | 1 |
| KB-DESIGN-LAYOUT | タイムライン レイアウト定数 | 1 |
| KB-DESIGN-TOKENS | 配色デザイントークン(OKLCH) | 1 |
| KB-FFMPEG-CODEC | コピー白名簿(H.264/H.265, AAC/MP3/AC-3) | 1 |
| KB-FFMPEG-GRAMMAR | ffmpeg filter 文法(ラベル/null/lanczos/エンコーダ) | 1 |
| KB-FFMPEG-SEEK | シーク時の音声同期ポリシー | **1** ← 本ループで更新 |

## 稼働部品の S-BOM
| 部品 | 種別 | 外部知識依存 | 受入深さ | build | 影響時の再検査 |
|---|---|---|---|---|---|
| Split ドメイン(SplitAt 等) | 核 | KB-CSHARP-IMMUTABLE | unit | loop-01.5 v2 | unit |
| Timeline 幾何(Layout) | 核 | KB-DESIGN-LAYOUT | unit | loop-03 | unit |
| Timeline 描画(配色) | 表面 | KB-DESIGN-TOKENS | golden+承認 | loop-03 | golden |
| ExportPlan.Analyze | 核(規則) | KB-FFMPEG-CODEC | unit/L2 | loop-02 | unit |
| Export filter/args(非シーク) | 表面 | KB-FFMPEG-GRAMMAR | L2 | loop-02 | L2 |
| **Export filter/args(シーク経路)** | 表面 | KB-FFMPEG-GRAMMAR, **KB-FFMPEG-SEEK** | L2 + **L3(音声同期)** | loop-02(CHEAT-008修正済=2入力・絶対時刻) | **L3 audio signal** |

要点: 「シーク経路」だけが **KB-FFMPEG-SEEK** に依存し、かつ受入深さに **L3** を持つ。この2列が劣化イベントの絞り込みを可能にする。
