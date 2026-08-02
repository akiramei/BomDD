# ECO-027 — deprecated 参照の掃討 lint(T0-15 昇格裁定の実装)

> 状態: **起票(2026-08-02)**。gate ① 承認= 2026-08-02 maintainer 採択
> 「本文は触らない・台帳の棚卸しと裁定済み残宿題を消化する」(2026-08-02 台帳棚卸し工程節・
> to-ECO 2 件のうちの 2 件目)。出典= EXP-202607-10。昇格裁定= 2026-07-08 T0 還元・改善 7
> 「deprecated 参照の掃討 lint を昇格裁定(§13): T0-15 が 2 例目 — 実装は次の機会
> (3 例目を待たない)」。baseline= a41bd61(ECO-026 accept)。

## §1 症状(実測 2 例+起票時予備測定)

**「正典を差し替えても誘導が旧を指し続ける」**(playbook §13 の改訂波及漏れ様式):

- 1 例目(Phase 1.5 還元・教訓 4): 判定表が deprecated を指したまま残存(判定表 1 件+
  ログ 2 本 3 箇所+playbook §1 自身の未追随を波及監査が検出)。
- 2 例目(transfer-01 T0-15・2026-07-08): phase2-spec が deprecated の旧一発変換
  (ui-mock-to-ui-bom.md)を指したまま — fresh 読者 3 体の静的検査で検出。
- **起票時予備測定(2026-08-02・読み取り専用)**: 同欠陥クラスの現存 2 件を先取り検出 —
  ①**リポ表玄関 README.md L21 が deprecated の旧一発変換を「抽出AIへの指示」として現役誘導**
  (Phase 1.5 二段プロンプトへの導線がトップ README に無い — T0-15 の再演がフロント文書で
  現存)②templates/ui-mock-extraction/README.md L47 が「経過措置」の語のみで参照
  (deprecated であることが読者に不可視)。

## 裁定(gate ① — 2026-08-02)

maintainer 採択「裁定済み残宿題を消化する」を製造承認とする。設計裁定(起票時確定):

1. **宣言規約= in-file マーカー**(実在標本較正 — harness ECO-006 教訓 6): deprecated 宣言は
   当該ファイル自身の行 `> **deprecated` を正本とする(実在標本= method/prompts/
   ui-mock-to-ui-bom.md:3 の既存様式をそのまま規約化 — 新形式を発明しない)。
2. **判定規則= 同一行の deprecated 語**: deprecated ファイルの basename を含む行は、
   同一行に `deprecated` の語を含む場合のみ「承知の参照」(索引・誘導回避の記述)として許容。
   含まない行は**現役誘導とみなし FAIL**。機械で「誘導」と「言及」を意味論的に区別しない —
   単純規則+是正で運用する(過剰工学の回避)。
3. **証拠台帳は対象外**: method/improvements.md・FINDINGS.md は過去状態の記述が本文の
   証拠正本であり、履歴記述を「現役誘導」と誤検出する — スコープから除外し、除外根拠を
   docstring へ宣言する(境界の値と端点の記録 — OBS-20260727-05)。走査対象= リポ直下 *.md
   (improvements/FINDINGS 除く)+method/**/*.md(improvements.md 除く)。
3'. 既知限界(宣言+掃射手段): basename の行内一致であるため、同名別ファイルがあると
   誤検出しうる(現状 deprecated は 1 件・衝突なし)。bomdd/ 台帳・.claude/skills は対象外
   (台帳= 履歴・skills= ハーネス面。skills の参照は必要が実測されてから拡張)。
4. **zero-declaration の意味論**: deprecated 宣言 0 件は「適用対象なし」の明示記録つき PASS
   (任意対象 — control-plan 空集合規則)。corpus 列挙 0 件は FAIL(対象欠落チャレンジ)。
5. **陽性対照を毎回実測**: 合成 corpus(宣言ファイル+naive 参照+knowing 参照)で
   「検出する/許容する」の両方向を毎回確認(検出器の生死判定)。

## 是正方針

1. **self-conformance C15 新設**(deprecated 参照の掃討 lint)— 裁定 1〜5 のとおり。
2. **予備測定の 2 件を是正**: ①README.md L21 の誘導を Phase 1.5 二段プロンプト
   (ui-raw-to-candidates → ui-apply-rulings-to-bom)へ差し替え ②ui-mock-extraction/
   README.md L47 に deprecated の明示を追加(経過措置の位置づけは維持)。

## 影響分析(製造前凍結)

- 変更ファイル= method/tools/self-conformance.py(C15 追加のみ)・README.md(L21 誘導差し替え)・
  method/templates/ui-mock-extraction/README.md(L47 明示追加)・台帳。
- 影響なし予測= 上記以外の md・bomdd-init.py・テンプレ設置機構は diff ゼロ。C1〜C14 の判定は
  不変。README のスキル本数表記(C7)に触れない。

## 受入基準(起票時凍結)

- V1: C15 実 corpus PASS(宣言 1 件・naive 参照 0 件)— 是正 2 件の反映後。
- V2: 陽性対照 — 合成 naive 参照の検出+合成 knowing 参照の許容+宣言 0 件時の明示記録 PASS。
- V3: 是正前の実 corpus で C15 が README.md L21 を検出する(赤の実測 — 是正ゲートの較正)。
- V4: 回帰= self-conformance C1〜C14 全 PASS(C15 込みで全緑)。
- V5: CI 緑(対象 revision・push 後に結論確認)。

## 製造・検証記録(2026-08-02)

- baseline の訂正: 起票時記載 a41bd61 の後に ECO-026 の CI 赤是正(fix2 c265e7a・窓更新
  d21b0a9)が挟まったため、**是正開始直前= d21b0a9** を diff 窓の baseline とする(ECO-026 の
  窓との重複を作らない)。
- **V3(赤の実測)= 予測完全一致**: 是正前 corpus で C15 FAIL — naive 参照 2 件
  (`README.md:21` / `method/templates/ui-mock-extraction/README.md:47`)・陽性対照 True。
  起票時予備測定と同一集合(新規検出 0・取りこぼし 0)。
- 是正: ①README.md L21 の誘導を二段プロンプト(ui-raw-to-candidates →
  ui-apply-rulings-to-bom)へ差し替え+旧一発変換の deprecated 明示(リンク 2 本は C13 の
  追跡集合検査を通過)②ui-mock-extraction/README.md L47 へ **deprecated** 明示を追加
  (経過措置の位置づけは維持)。
- **V1= C15 PASS**(宣言 1 件・naive 0 件・陽性対照 True)。**V2= 陽性対照 実測**
  (合成 naive の検出〔`naive.md:1` を厳密一致で〕+合成 knowing の許容 — 毎回実行される
  常設対照。宣言 0 件時の明示記録 PASS は合成 corpus の分岐設計で担保・実 corpus は宣言 1 件)。
- **V4= self-conformance C1〜C15 全 PASS**(exit 0・C13 は README の新リンク 2 本込みで
  192 links 不在 0)。
- V5(CI)= push 後に追記。

### 併記(ECO-026 の CI 追記)

fix2 以降の CI 結論= **d21b0a9 緑**(self-conformance: success・2026-08-02)。ECO-026 の
V5 はこれでクローズ(中間 commit c265e7a/cd81e88 は単独 push なし= run 不在= UNKNOWN・
対象 revision は緑実測 — ECO-025 と同じ 4 値記載)。
