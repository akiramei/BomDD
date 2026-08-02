# equip-03 protocol(**draft** — gate ① 裁定待ち・凍結前)

- 起草: 2026-08-02(equip-02 外部レビュー裁定 5「次回 Opus 5 は実在 BOM への ECO 適用製造」の適用)
- 状態: **未凍結**。maintainer の gate ① 裁定(下記 §8)の後に凍結 commit し、以後本文を変更しない。

## 1. 目的

claude-opus-5 の **ECO 適用製造クラス**の初測定(equip-02 の P2〔固定 BOM 新規製造〕に続く
第 2 セル)。評価するのは新規製造能力ではなく、レビュー裁定 5 の 4 次元:

1. **影響範囲の抽出** — under/over-inclusion(impact-retrospective+R-052 diff 監査で機械実測)
2. **変更対象外の非破壊** — 既存オラクル・全テスト・self-hosting lint・ViewPrism2 workspace 回帰
3. **BOM/as-built の同期** — 変更後の台帳整合(as-built・register 記帳の正確性)
4. **証拠を残して変更を閉じる** — diff_audit(baseline→head アンカー)での窓閉鎖・order 完備

## 2. 題材(実在・未起票の Plm ECO 候補)

**Plm ECO-006(仮)**: `repo:` 形パス参照の repo 不在を R-004(error)でなく X-XREPO 系
skip(info)へ — ID 参照の cross_repo(候補リポ不在= skip)との一貫性回復。

- 出典: BomDD-Plm bomdd/52-metrics.yaml `product_eco_candidates`(2026-07-03 記録・解消マーカー
  なしの現存候補)。実害実測: ViewPrism2 pre-commit 常駐で正当な cross-repo 参照 7 件が error
  (当面の運用= workspace 宣言で回避中)。
- 性質: src 変更+ルール意味論+オラクル拡張+影響分析を伴う変更製造 — 測定 4 次元を全て通過する。
- 人工課題ではない(録済みの実需)。

## 3. 比較セル(既存)

Plm eco_001(opus-4.8= 27/27 / sonnet-4.5= 27/27)・eco_002(opus-4.8 / sonnet-4.5 とも 33/33)
— 同一リポ・同一測定系(較正→凍結オラクル→全再認証)の ECO 適用多工場前例。
比較は工程指標(oracle・self_acceptance・unnecessary_modification・cheats・under/over-inclusion)
で行い、率の統計判定はしない(equip-01 凍結裁定の継承)。

## 4. 役割分担(三層検査 — equip-02 レビュー裁定 4 の様式化)

| 役割 | 担当 | 扱い |
|---|---|---|
| 設計者側(起票・オラクル拡張・較正の凍結) | 主観察者(claude-fable-5)+maintainer 裁定 | 測定系 — 工場の成果物に含めない |
| 工場(被測定設備) | claude-opus-5(Agent subagent・equip-02 と同一構成) | 影響分析起草→製造→自己受入→as-built 起草 |
| 固定契約の合否 | 機械(凍結オラクル+全テスト+self-hosting lint) | 合否の主証拠 |
| BOM・工程適合の独立検査 | 別ベンダー AI(Codex fresh・read-only・情報遮断) | **EXP-20260726-01(別ベンダー検査軸)の 2 回目を兼ねる** |
| 解釈・裁定 | 人間(maintainer) | gate 裁定+意見不一致時+golden |

工場の自作検査は独立検査に数えない(equip-02 裁定 4)。

## 5. 入力固定(EXP-20260802-06 の初適用)

protocol 凍結時に固定: 入力 tag 名+expected_commit+**input_tree_hash**+オラクル成果物 hash+
prompt bundle sha256+ハーネス構成。実行開始時の解決値と不一致なら **fail-closed(開始しない)**。

## 6. 設備・記録(ECO-028 様式+equip-02 実績の継承)

requested(Agent `model: "opus"`)/resolved(self-reported・unknown 規律)/harness/主観察者/
時間分解(壁時計+区間)/トークン(取得可能分)/費用(unknown 可・推定禁止)/
介入・差戻・範囲外の 3 カウンタ。二車線(OBS-20260802-07): 必須製造車線の合否は凍結受入のみで
判定し、自主拡張(追加検査・変異検査・残渣指摘)は別枠観測 — 救済に使わない。
BOM/Control Plan 自体の変更提案は工場権限外(人間承認必須)。

## 7. 手順(概要 — 凍結時に詳細化)

1. Plm へ ECO-006 起票(order+裁定点整理)→ **gate ① maintainer 承認**
2. 設計者側: オラクル拡張(X-XREPO 分岐の較正 — 変更前個体で FAIL 確認)→ 入力固定(§5)
3. 工場: 影響分析起草 → 製造 → 自己受入 → as-built 起草(介入 0 原則・全記録)
4. 機械受入: 凍結オラクル全数+全テスト+self-hosting --eco+ViewPrism2 workspace 回帰
5. 独立検査: Codex fresh(read-only・情報遮断)→ 突合・カウンタ記帳
6. maintainer 裁定・golden → verified → 窓閉鎖(head アンカー)→ 測定記録・還元候補記帳

## 8. 裁定点(gate ① — maintainer)

1. **題材の確定**: ECO-006(X-XREPO 一貫性)で良いか。
2. **工場スコープ**: 影響分析(61 相当)の起草を工場に含める(推奨 — 測定次元 1 の直接測定)か、
   設計者側で書くか。
3. **独立検査の採否**: Codex fresh を入れる(推奨 — EXP-20260726-01 の 2 回目を兼ねて一石二鳥)か、
   機械受入のみか。
4. **便乗の採否**: M-BOM 写像被覆ギャップ(unmapped 76 files・単独 ECO は過剰と記録済み)の
   32-mbom 所有宣言を本 ECO へ載せるか(載せる場合の受入= impact-retrospective の
   unmapped_files 0 — 測定次元 3〔BOM 同期〕の測定面が広がる。ただしスコープ増)。

## 9. 採らないもの

- 本ラウンドから資格制度・routing 基準は導出しない(凍結裁定のトリガー待ち — equip-02 裁定 6)。
- webapi-02 セルの反復はしない(再現性測定は別目的として将来判断)。
