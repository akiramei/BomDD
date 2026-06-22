# 手法改善ログ(method evolution)

Loop 総括で出た改善提案と、各 Loop で**実際に適用**したもの。改善は「ずるが減ったか」で効果測定する。

## Loop 1 で提案された改善(loop-01-report.md より)
1. 受入オラクルの完全性定義(全数値ACに丸め方式・誤差許容・中間値/境界テストベクタ必須) — 対 CHEAT-005
2. E-BOM を木→グラフ(共有/横断部品を owner/consumers 付きで表現) — 対 CHEAT-002
3. ③の前に受入基準の無矛盾性検査工程(identity 等の標準ポリシー常設) — 対 CHEAT-004
4. リバース工程の定義(双方向トレースのカバレッジ証明) — 対 CHEAT-001
5. 受入モダリティ列(unit/golden/interaction/manual)を M-BOM に追加 — 対 CHEAT-006
6. 製造装置に「慣習で埋めた箇所」の報告を義務化 — 対 C2(暗黙知)

## Loop 1.5 で適用する改善
**①②③ を本適用、⑤⑥ を軽量適用**(④は Loop2 以降)。

- **①(完全性)**: M-BOM の AC-5 に丸め方式を明記 — `SnapFrame` は最近接フレーム、**中間値は偶数側(MidpointRounding.ToEven=.NET Math.Round 既定。原版準拠)**。
  オラクルに**中間値テストベクタ**を追加(`SnapFrame(0.25,2)=0.0`, `SnapFrame(1.25,2)=1.0`)。これで丸め次元の未指定をゼロにする。
- **②(グラフ)**: E-BOM を製品部品グラフ + サブグラフ抽出として再表現([loops/loop-01.5-split/02-ebom-graph.md])。横断部品に owner/consumers を付与。
- **③(無矛盾性)**: M-BOM 作成後に AC の無矛盾性を検査。AC-12 を**単一ポリシー**へ — 「構築時 max(Id)+1 で初期化した永続カウンタから払い出し、Split 成功ごとに+1、Undo/Redo で巻き戻さない」。
- **⑤(モダリティ)**: AC 表に「検査モダリティ」列(unit/golden/interaction/manual)を追加。manual は不足として可視化。
  - **⑤改(Loop2.5 で精緻化)**: 外部ツール成果物の受入は深さの梯子で表す — `L0文字列照合 < L1存在/終了コード < L2メタデータ(ffprobe等) < L3内容/信号(PSNR/相関)`。深いほど忠実・高コスト。AC ごとに必要深さを指定。純粋ロジック=unit(L0相当の客観)、外部ツール=既定L2以上、知覚/同期=L3。実証: execution(L2)が Lossless 別コーデックを捕え、文字列照合(L0)の様式誤検出を消した(loop-02.5)。
- **⑥(慣習報告)**: 製造装置への指示に「BOMに無く慣習で埋めた箇所」の網羅報告を正式工程として明記(Loop1 と同様)。

## 効果測定(Loop 1 → 1.5)
| 指標 | Loop 1 | Loop 1.5 目標 |
|---|---|---|
| 従来手法の介入回数 | 1(CHEAT-004 修正) | 0 |
| サイレント乖離(被覆次元) | 1(CHEAT-005 丸め) | 0(中間値テストで被覆) |
| 1回目オラクル合格 | 13/14 | 全green(1回目) |
| 発散を生んだギャップ | 2 | 0(目標) |

## 2026-06 corrective improvement — 表示 omission defect escape / CAPA 経路逸脱
観測:
- 製造後のユーザー確認で、原典 UI に存在した表示要素が仕様/BOM/検査から漏れていたことが発覚した。これは発生(Occurrence)ではなく検出(Detection)の流出であり、凍結後の工場・固定オラクルは原典を見ないため下流では原理的に検出できなかった。
- 指摘後、設計者 AI がまず直接ソース修正へ進み、仕様→E-BOM→M-BOM→Control Plan→再製造の是正経路を迂回した。

適用した改善:
1. `silence-checklist.md` に **表示要素集合・原典表示パリティ** を追加。原典あり UI/帳票 surface は、提示フィールド・ラベル・サムネイル・ファイル名・状態表示を全数トレースする。
2. `20-spec.md` / `30-ebom.yaml` / `32-mbom.yaml` / `33-control-plan.yaml` / `41-fixed-oracle.yaml` に表示契約と凍結前パリティサインオフを追加。
3. `bomdd-playbook-v1.md` と `phase5-accept.md` に **不具合発覚後の直接ソース修正禁止** と帰属分類(`spec_omission / bom_sync_gap / oracle_gap / manufacturing_miss / harness_bug`)を追加。
4. `60-change-order.md` / `61-impact-analysis.md` / `phase7-change-order.md` を ECO だけでなく CAPA(欠陥是正)の再入口として拡張。

期待する効果:
- 原典比較でしか検出できないパリティ欠陥を G2/G2' の凍結前で止める。
- ユーザー指摘後の修正をソース直しではなく、上流成果物の改訂・同期・fresh factory 再製造へ戻す。
