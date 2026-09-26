# Change Order — ECO-084(運転実証の kit 是正 2 件: 初回製造の起票規則〔change-management §0〕+工場隔離の手段〔factory-delegate 工程 2〕)

> 指示: user 2026-09-26 DECIDE「1:A 2:A」(運転実証 EXP-20260922-02 の帰結・BomDD-UnitConv-Sample の 3 ECO 実測)。
> **起票と製造を同一 commit で行う**(文書のみ・ECO-076/082/083 の型)。受入は製造者較正のみ。verified 昇格は self-conformance PASS と CI 結論を観測した後の受入 commit で。

## 担当設備(equipment)

- 起票・製造: requested/resolved `claude-fable-5-1`・Claude Code(Claude Agent SDK)・来歴 **self-reported**
- producer: EQ-001
- 独立検査: なし(文書のみ・製造者較正のみ。inspector 行は置かない)

## 0. 実測(起票根拠)

- **停止 1 件(2026-09-22・BomDD-UnitConv-Sample)**: forward 初回製造の commit を process-core の hook が E01(保護パス `src/`・`test/` に open ECO なし)で遮断。kit の
  `product-profile/change-management.md` §0(:10-11)「初回製造は forward Phase 0〜6 であり ECO は使わない」と `process-core/process-profile.yaml`(:19)`protected_paths: [src/, test/, tests/]`(導入点から強制)が矛盾。
  運転員の処置= 初回製造を ECO-001 として起票(起票 commit → 製造 commit)で通過。OBS-20260922-02(1/3)。
- **隔離の手段の欠落(4 回/4 製造)**: `prompts/phase4-manufacture.md`(:9)と factory-delegate は「渡してはならないもの」を列挙するが、Codex CLI(workspace-write・作業木全体が可読)で
  **渡さない手段**を書いていない。運転員が memory から「非開示物を製造中だけ作業木外へ退避し、製造後に復元」を 4 回持ち込んだ(improvements.md 2026-09-26 節 ③・一般化検査 (a))。
- user 裁定(2026-09-26): 1:A(手順を機構に合わせる・§0 に 1 行)/ 2:A(factory-delegate 工程 2 に手段の 1 段落)。B 案(機構側の免除・phase4 プロンプト側)は採らず。

## 1. 変更要求(凍結・文書のみ)

1. `method/templates/product-profile/change-management.md` §0: 「ECO は使わない」の直後に 1 文追記 — 「ただし process-core(保護パス)を設置済みのリポでは、初回製造の成果物を保護パスへ置く commit も
   open な ECO を要求する(E01)。その場合は初回製造を **ECO-001 として起票してから**製造 commit を行う(起票 commit が先・同一 commit 起票は不可)。」
2. `method/templates/product-profile/skills/factory-delegate.md` 工程 2: 末尾に「**隔離の手段**」1 段落 — 工場が作業木全体を読める経路(Codex CLI workspace-write 等)では「渡さない」の指示だけでは
   隔離にならないので、非開示物(`41-*`・`42-*`・`jigs/`・`reports/`・`00-*`・`10-*`・`50〜53`・検査結果 JSON・`bomdd-kit/`・`.claude/`・`AGENTS.md`・`CLAUDE.md`)を**製造中だけ作業木外(OS temp)へ退避**し、
   製造後に戻す(git 追跡物は `git checkout -- <path>` でも復元可)。退避物は受入 commit に含めない。工場には「読まない」と併記し、報告に「読んだファイル一覧」を求める(申告と手段の二重)。
3. `.claude/skills/factory-delegate/SKILL.md` を正本と同期(同じ 1 段落・既知の差分〔冒頭注記・`{{METHOD}}` 解決〕は不変)。
4. `method/improvements.md` に本節(OBS-20260922-02 → recovered・一般化検査 (a) → 織り込み済み)。

**採らない**: process-profile の導入点免除(1:B)/ phase4 プロンプトへの記述(2:B・製品の書き手は kit の prompts より skill を先に読む実測)/ product-profile/change-management.md 以外の
change-management 記述(製品リポの既存写しは kit 再設置まで非波及)/ 退避の自動化スクリプト(手段の文書化のみ・機構は足さない)。

## 2. 影響なし予測(製造前・凍結)

diff= change-management.md(1 文)・factory-delegate 正本と写し(1 段落)・improvements.md+台帳系(order・register)のみ。bomdd-init の SKILLS 13 不変・activation-map 不変・process-core diff 0・
C4/C7/C12/C13 不変・写しと正本の差分出力は変更前と一致・tools/hooks/.github diff 0・警告 0。

## 3. 受入条件(製造前に凍結・二部形)

- V1(条件): change-management.md §0 に `ECO-001 として起票してから` が 1 件あり、その行が「初回納品後」の段落内(§1 見出しより前)にあること — 検査法: grep -n。
- V2(条件): factory-delegate 正本と写しの両方に `隔離の手段` が 1 件あり、その行が「### 工程 2」より後・「### 工程 3」より前にあること。写しと正本の差分出力が変更前と byte 一致すること — 検査法: grep -n・diff。
- V3(条件): self-conformance 全 PASS(exit 0 観測後に commit)・CI success・diff 窓= allowed_paths のみであること — 検査法: 単一入口・`gh run list --commit <full sha>`・`git diff --stat baseline..head`。
- V4(条件): 製造者較正のみ・較正 receipt(trigger ①: verified 昇格)があること。

## /preflight receipt(起動経路: **job 経由** — `bomdd-job.py ECO-084` の出力を開始 artifact として読んだ)

- 分類= 既裁定の適用実装(user DECIDE 1:A 2:A)。baseline `1f5b76b`= **confirmed**(作業木 clean・push 済み)/ 次番 084= **confirmed**(register に id 0 件)/ 是正箇所の実在= **confirmed**(§0 の行番号実読)/
  同一ファイルへの進行中 ECO がないこと= **confirmed**(ECO-083 は verified・進行中 ECO なし)/ 写しの同期状態= **confirmed**(変更前 diff= 冒頭注記+`{{METHOD}}` 2 行のみ)。
- 開始判定: **PROCEED**・override 0。

## 4. 製造と受入の実測(2026-09-26・同一 commit)

- 製造物: change-management.md §0 の 1 文 / factory-delegate 正本・写しの「隔離の手段」1 段落 / improvements.md 節。製造中の発見 0 件。
- **V1**= PASS(観測: change-management.md の `ECO-001 として起票してから` 1 件= 13 行目・§1 見出し 15 行目より前)。
- **V2**= PASS(観測: `隔離の手段` 正本 88 行〔工程 2= 72・工程 3= 93〕/ 写し 92 行〔76・97〕・各 1 件。写しと正本の diff= 冒頭注記+playbook パスの既知 8 行のみ= 変更前と一致)。
- **V3**= §5 で記録(観測後)。

## 5. クローズ(2026-09-26・verified・製造者較正のみ)

- **V3**= PASS(観測: stage 後に self-conformance → **exit=0 全 PASS** → witness(tree 8c1a0a5c85f0・gates 1・producer EQ-001)→ 入口 dry `ADVANCE ECO-084 OK` → 製造 commit e30eb2a → push → CI run 36207193259 **success**)。
  diff 監査の窓: baseline `1f5b76b` → head `e30eb2a`(**窓閉鎖**・受入 commit は台帳系のみ)。窓内= allowed_paths の 6 ファイルのみ(`git diff --stat 1f5b76b..e30eb2a`)。
- **V1/V2**= §4(PASS)。**V4**= 製造者較正のみ(独立検査なし)・下の較正 receipt。register: `implemented → verified`・head 凍結。
- **到達点**: 運転実証で運転員が持ち込んだ手段 2 つ(初回製造の起票・非開示物の退避)が kit の文書に入り、次の製品リポは bomdd-init の配布物だけでこの 2 点を持つ。

### 較正 receipt(/calibrate 自己適用 — trigger ①: verified 昇格・receipt_author_role= producer。文書のみの変更)

- 査定した主張と判定:
  1. 「§0 の起票規則と工程 2 の隔離の手段が正本・写しに入った」— **observed / 適格**(grep・V1/V2・写しの diff は既知 8 行)。
  2. 「文書化した手段は実証で機能したものと同一」— **observed / 条件付き適格**(実証 4 回の退避手順を文章化した。次の製品リポで文書だけを読んだ運転員が同じ手順を取るかは未測定)。
  3. 「起票規則は process-core の E01 と整合する」— **observed / 適格**(実証で ECO-001 起票 → 製造 commit の順で E01 を通過した実測に基づく・validator は非改変)。
- 検出した計器欠陥(帰属つき): なし。
- 検出力の限界: 文書の効果(次の製品での持ち込み 0 回)は未測定・独立検査なし・改訂した change-management.md は既存製品リポの写しへは kit 再設置まで届かない。
- battery 行別記録:

  | Q | asked/NA | 判定 | 実測 or 読解 | 所見 |
  |---|---|---|---|---|
  | Q1 | asked | observed/適格 | 実測 | 条件は grep と diff が測る範囲・主張 2 は「条件付き」で効果を主張しない |
  | Q2 | asked | observed/適格 | 実測 | known-bad= 変更前(grep 0 件)・known-good= 変更後(1 件) |
  | Q3 | asked | observed/適格 | 実測 | 変更前(手段なし・運転員の memory)→ 変更後(文書 1 文+1 段落) |
  | Q4 | asked | observed/適格 | 実測 | 実ファイル・写しの実 diff |
  | Q5 | asked | observed/適格 | 実測 | 未測定(次の製品での効果)を宣言 |
  | Q6 | asked | observed/適格 | 実測 | 検査 exit 観測 → witness → 入口 dry → commit → push → CI |
  | Q7 | asked | observed/適格 | 実測 | 陽性対照= 変更前の grep 0 件 |
  | Q8 | NA | — | — | 免除機構なし |
  | Q9 | asked | observed/適格 | 実測 | witness・register・run 台帳・order |
  | Q10 | asked | 宣言 | 読解 | 上記「検出力の限界」 |
  | Q11 | asked | observed/適格 | 読解 | 入力クラス= 起票規則 / 隔離の手段 / 写し同期 |

- このクローズが支持しないもの: 次の製品リポでの持ち込み 0 回(効果)/ 既存製品リポへの波及(kit 再設置まで)/ 隔離の手段の他ハーネスでの妥当性(Codex CLI 以外は未測定)。
