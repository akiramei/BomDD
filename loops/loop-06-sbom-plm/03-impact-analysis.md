# ③ 影響分析 — KB-FFMPEG-SEEK-001 を S-BOM で逆引き

## Step 1: 影響部品の絞り込み(S-BOM 逆引き)
KB-FFMPEG-SEEK に依存する部品を [01-sbom-baseline.md](01-sbom-baseline.md) から逆引き:

| 部品 | KB-FFMPEG-SEEK 依存? | 判定 |
|---|---|---|
| Split ドメイン | × (KB-CSHARP) | **再検査不要** |
| Timeline 幾何 | × (KB-DESIGN-LAYOUT) | **再検査不要** |
| Timeline 描画 | × (KB-DESIGN-TOKENS) | **再検査不要** |
| ExportPlan.Analyze | × (KB-FFMPEG-CODEC) | **再検査不要** |
| Export filter/args(非シーク) | × (KB-FFMPEG-GRAMMAR のみ) | **再検査不要** |
| **Export filter/args(シーク経路)** | ✓ (KB-FFMPEG-GRAMMAR, **KB-FFMPEG-SEEK**) | **再検査対象** |

→ **6部品中1部品のみが影響**(83% を再検査から除外)。核は全て対象外。Export の中でも非シーク経路は除外。

## Step 2: 再検査の深さ
シーク経路の受入深さ = **L2 + L3(音声同期)**。本イベントは同期保証の更新なので **L3 が必須**。
L2 は不適(Loop5: correct と buggy は尺5.00s・コーデック同一でL2では区別不能)。シナリオ = SC4(seek)。

## Step 3: 再検査の実行(L3 治具, loop-05)
| 想定 build | 構造(v2準拠?) | L3 音声内容 | 交換判断 |
|---|---|---|---|
| **現build**(loop-02 修正済=2入力・絶対) | ✓ 準拠 | 内容OK(800-1200Hz) | **K-BOM更新のみ(再認証)・再製造不要** |
| 仮: buggy(座標系誤) | ✓構造のみ | ★誤位置(300-700Hz) | **再製造必要** |
| 仮: phaseA(単一入力・相対) | ✗ 非準拠(1入力) | 内容OK | **再製造必要(構造準拠のため)** |

## Step 4: 二次発見 — 治具(fixture)も劣化対象
v2 は**サンプル精度同期**を要求するが、L3治具は1秒/100Hz粒度で粗い。
- 現build/phaseA はいずれも L3「内容OK」だが、phaseA の AAC サブms ドリフトは**この粒度では検証不能**。
- よって phaseA は L3内容だけでは v2 認証不可 → **構造準拠(2入力必須)へフォールバック**して再製造判断。
- 含意: 知識更新は「どの部品を再検査するか」だけでなく「**必要な検査の深さ・許容差**」も上げ得る。
  治具(±ms 相関への精緻化)も保守対象。これは「治具を成果物管理」(#6)の保守版。
