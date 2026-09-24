# Change Order — ECO-083(factory-delegate の経緯節「この委譲自体の教訓」を除去し、生きた規則 1 件を工程 6 へ移す+見出し「絶対規律」→「規律」の同乗)

> 指示: user 2026-09-24「所見3も適用して」(/claude-api prompt-audit 所見 3)。同乗: 同日の user 裁定「2:C」(所見 5 の残り= 正本 4 ファイルの見出し「絶対規律」は
> 単独起票せず、次にその正本を触る ECO へ同乗)— 本 ECO が触るのは factory-delegate のみなので、同乗は factory-delegate の 1 見出しに限る(sec-advisory・eco-file・bomdd-next は対象外のまま)。
> **起票と製造を同一 commit で行う**(文書のみ・ECO-076/082 の型)。受入は製造者較正のみ。verified 昇格は self-conformance PASS と CI 結論を観測した後の受入 commit で。

## 担当設備(equipment)

- 起票・製造: requested/resolved `claude-opus-5-5`・Claude Code(Claude Agent SDK)・来歴 **self-reported**
- producer: EQ-004
- 独立検査: なし(文書のみ・製造者較正のみ。inspector 行は置かない)

## 0. 実測(起票根拠)

- **監査所見 3**(2026-09-24・/claude-api prompt-audit・基準モデル Claude Opus 5.5): `factory-delegate.md` 末尾の節「この委譲自体の教訓(ECO-137 から)」は事故の経緯を語る節で、
  スキルが呼ばれるたびに読み込まれる。4 項目の照合(実読):
  1. 「正本委譲は機能した」— 規則は「規律」節の **正本委譲** に既にある(経緯のみ)。
  2. 「完了バリアの不在が最大の失敗 → 工程 3 を必須化」— 規則は **工程 3**(製造完了バリア)と「規律」節の **完了バリア前に検査しない** に既にある。
  3. 「/codex status は一次判定に使えない」— 規則は **工程 2**(返り値の task-id を信用しない)と **工程 3**(status の completed を信用せずツリーで判定)に既にある。
  4. 「golden n/a の意味」(挙動 bit 一致+視覚変更なし= 照合対象なし・「修正が些末」ではない・性能 ECO での golden 不要の型)— **他のどこにも無い**生きた規則。
- **見出し「絶対規律」**: 各項目に理由が併記済みで「絶対」は重みの情報を足さない(監査所見 5)。正本の変更には ECO が要るため、裁定「2:C」で本 ECO に同乗。

## 1. 変更要求(凍結・文書のみ)

1. `method/templates/product-profile/skills/factory-delegate.md`: 節「この委譲自体の教訓(ECO-137 から)」とその直前の区切り線 `---` を削除。
2. 同: 項目 4(golden n/a の意味)を **工程 6**(lifecycle クローズ)の accept 行の直後へ 1 項目として移す(文意は不変)。
3. 同: 見出し「## 絶対規律」→「## 規律」。
4. `.claude/skills/factory-delegate/SKILL.md` を正本と同期(同じ 3 箇所・既知の差分〔frontmatter と冒頭注記・`{{METHOD}}` 解決〕は不変)。
5. `method/improvements.md` に本節(効果の新規 EXP は置かない — §5 の理由)。

**採らない**: 他の経緯記述(規律・工程内の「ECO-137 で…」の括弧書き — 規則の理由として機能している)/ 工程 2 の Codex 経路の具体(版に依存するが壊れやすい操作の手順として妥当・所見 8 は記録のみ)/
工程 4 の `dotnet build` 直書き(所見 9・範囲外)/ sec-advisory・eco-file・bomdd-next の見出し(本 ECO は触らない)。

## 2. 影響なし予測(製造前・凍結)

diff= skills 正本・写し・improvements.md+台帳系(order・register)のみ。bomdd-init の SKILLS 13 不変・activation-map 不変・C7/C12/C13 リンク先不変・tools/hooks/.github diff 0・
写しと正本の差分出力は変更前と一致・worklist 新規 ID 0・警告 0。

## 3. 受入条件(製造前に凍結・二部形)

- V1(条件): 正本と写しの両方で `この委譲自体の教訓` 0 件・`## 絶対規律` 0 件・`## 規律` 1 件・`golden n/a は` 1 件で、その行が「### 工程 6」見出しより後にあること — 検査法: grep -n。
- V2(条件): 削除した 4 項目のうち 1〜3 の規則が残存箇所に実在すること(`正本委譲`・`完了バリア前に検査しない`・`返り値の task-id は信用しない`・`/codex:status` の "completed" を信用せず)で、
  写しと正本の差分出力が変更前と一致すること — 検査法: grep・diff。
- V3(条件): self-conformance 全 PASS(exit 0 観測後に commit)・CI success・diff 窓= allowed_paths のみであること — 検査法: 単一入口・`gh run list --commit <full sha>`・`git diff --stat baseline..head`。
- V4(条件): 製造者較正のみ・較正 receipt(trigger ①: verified 昇格)があること。

## /preflight receipt(起動経路: **job 経由** — `bomdd-job.py ECO-083` の出力を開始 artifact として読んだ)

- 分類= 既裁定の適用実装(user 指示「所見3も適用して」+裁定「2:C」の同乗)。baseline `1bf213a`= **confirmed**(作業木 clean・push 済み・ECO-082 verified)/ 次番 083= **confirmed**(register に id 0 件)/
  削除節の 4 項目と残存規則の対応= **confirmed**(§0 の実読)/ 削除節への参照が他ファイルに無いこと= **confirmed**(grep: 見出し文字列の一致は正本と写しのみ・improvements.md:6696 は ECO-137 の 3 規律への言及で本節の参照ではない)/
  同一ファイルへの進行中 ECO がないこと= **confirmed**(進行中は ECO-079〔implemented〕のみで allowed_paths に factory-delegate・improvements.md を含まない)。
- 開始判定: **PROCEED**・override 0。

## 4. 製造と受入の実測(2026-09-24・同一 commit)

- 製造物: 正本と写しの 3 箇所(経緯節と直前の区切り線の削除・golden n/a の工程 6 への移設・見出し「規律」)/ improvements.md 節。製造中の発見 0 件。
- **V1**= PASS(観測: 正本・写しとも `この委譲自体の教訓` 0・`## 絶対規律` 0・`## 規律` 1・`- golden n/a は` 1〔正本 144 行 > 工程 6 見出し 138 行 / 写し 148 行 > 142 行〕)。
- **V2**= PASS(観測: 正本・写しとも `正本委譲` 3・`完了バリア前に検査しない` 1・`返り値の task-id は信用しない` 1・`` `/codex:status` の "completed" を信用せず `` 1 / 写しと正本の diff 出力が変更前と byte 一致)。
- **V3**= §5 で記録(観測後)。
