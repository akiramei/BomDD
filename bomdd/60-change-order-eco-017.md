# ECO-017 — qualification runner・bomdd-init・C11 の隔離と判定精度(独立検査 REV 5 件の是正)

> 状態: **verified(2026-07-26)**。fix= d8bfbea・検証 V1〜V3 全 PASS・窓は accept で閉鎖。

## 裁定(gate ① — 2026-07-26)

- 製造承認(2026-07-26・maintainer — 016/017 一括承認・017 は 016 verified 後に着手)。
  baseline を ECO-016 accept(c9ecfe7・是正開始直前)へ更新。
- 設計確定 3 点:
  1. **IQ-07 新設**= HEAD 実在(git 文脈で FAIL)。**worktree/index の clean は FAIL にせず観測
     記録**に留める — --skills-only の適格性確認は設置直後(未コミット)に走る正当経路があるため
     (是正方針の「clean index/worktree を追加」からの意図的縮小・理由記録)。
  2. E07 の実 Git 負例= 「登録なし ECO への trailer を持つ commit → validate が E07」。
     E04 の実 Git 負例= 3 状態 profile の sandbox(yaml 再構成)で fix trailer なし遷移。
  3. 決定性表示= runs=1 のとき「DET SKIP(未検証)」(PASS 偽装の排除)。full は --runs>=2 を
     argparse 強制。
> 出典: ECO-015 後追い独立受入検査(transfer-04 様式・Codex gpt-5.6-sol・REJECT)—
> bomdd/reports/independent-inspection-eco-015.md(真正判定 13/13 CONFIRMED・誤検出 0)。
> 本 ECO は runner・init・C11 系 5 件(REV-05/06/07/11/12)を是正する。validator 系 8 件は ECO-016。
> 順序依存: **ECO-016 適用後に製造**(受入が 016 後の validator を前提)。

## 起票(2026-07-26)

対象所見と是正方針:

1. **REV-05 — IQ 判定の近似**: IQ-03 は hooksPath を **git の解決規則で絶対化し、対象 root 配下の
   `bomdd/hooks` と正準比較**(`endswith` 廃止 — `C:/outside/bomdd/hooks` を拒否)。IQ-02 は
   substring でなく**設置 hash 照合または実行 probe**(hook が実際に validator を起動することの
   観測)。IQ-04 の Windows「判定対象外」は維持するが、対象外の理由と残余リスクを報告へ明示。
2. **REV-06 — bomdd-init の commit 失敗非致命**: 製品リポの git init/config/add/初回 commit の
   いずれかが失敗したら **exit 非 0**(「[git] 失敗表示のまま line ready PASS・exit 0」の
   不整合解消)。IQ へ **HEAD 実在+clean index/worktree** を追加。CI 等の意図的な
   git 設定なし環境向けには --no-git / --no-qualify の明示経路を案内(無音の救済をしない)。
3. **REV-07 — 不完全既存設備の保持扱い**: install_process_core を三状態判定へ —
   **新規(全部設置)/完全な既存(保持)/不完全な既存(FAIL・復旧手順の提示)**。
   ECO-009 #2(kit 完全性検査)の様式を process-core へ水平展開(同族穴の解消)。
   git リポでは fresh/既存にかかわらず qualification を実行(保持時も IQ は走る —
   既存設備の現在の健全性を測る)。
4. **REV-11 — 決定性・C11 判定の精度**: full qualification は **--runs >= 2 を argparse で強制**
   (0/負数の 1 回丸めによる DET PASS 偽装を排除。--mode iq/oq 単独は 1 回可)。C11 は
   **--json の構造化結果**から IQ-03 自身の `pass == false` を確認(文字列一致の廃止)し、
   2 回決定性も C11 内で回帰固定。**E04(3 状態 fix trailer)と E07(未知参照)の実 Git 負例**を
   OQ へ追加(3 状態 profile sandbox — selftest のみの被覆を実経路へ昇格)。
5. **REV-12 — sandbox 環境継承の隔離穴**: sandbox git 用の環境を **allowlist で構築**
   (または `GIT_DIR`/`GIT_WORK_TREE`/`GIT_INDEX_FILE`/`GIT_OBJECT_DIRECTORY`/
   `GIT_ALTERNATE_OBJECT_DIRECTORIES`/`GIT_CONFIG_COUNT|KEY|VALUE` 系を明示削除)。
   各 sandbox 操作前に **実 git dir/worktree が sandbox root 配下であることを実測**
   (hook 文脈からの起動= GIT_DIR 設定下でも sandbox 外へ書かない — 隔離の負例を追加)。

## 受入基準(事前登録 — 製造前に凍結する)

- 陽性対照: 正常 scaffold+qualification 全 PASS(ECO-016 適用後の validator と統合)
- 負例: hooksPath= 外部の `.../bomdd/hooks` → IQ-03 FAIL / hook 本文が validator 非起動(コメント
  のみ substring 一致)→ IQ-02 FAIL / git user なし環境の scaffold → bomdd-init exit 非 0
  (--no-git 明示時を除く)/ 空 `bomdd/hooks/` のみの既存リポへ --skills-only → FAIL+復旧手順 /
  --runs 0・負数 → argparse エラー / GIT_DIR を外部リポへ向けた状態で OQ → sandbox 外への
  書き込みゼロ(外部リポの status 不変を実測)/ E04・E07 の実 Git 負例が登録理由で拒否
- 決定性: full 2 回実行の判定・理由集合一致+C11 で回帰固定
- 回帰: self-conformance 全 PASS・C4 scaffold 形状不変・ECO-015 の既存 OQ 7 対照が引き続き PASS

## 影響分析(製造前予測 — 未凍結)

- 影響なし予測: `method/templates/process-core/tools/process-qualification.py`・
  `method/tools/bomdd-init.py`・`method/tools/self-conformance.py` 以外 diff ゼロ。
  正常系 scaffold の生成物は不変(判定の厳格化のみ)。REV-06 により **git 設定なし環境での
  bomdd-init の既定挙動が exit 0 → 非 0 へ変わる**(意図的変更 — CI 利用者は --no-git/--no-qualify
  を明示)。C11 の所要は 2 回決定性で微増(数秒)。
- 順序依存: ECO-016 verified 後に製造開始(diff 窓の分離)。

## スコープ外(明示)

- validator 本体の意味論(ECO-016)
- capture 等の製品依存設備・工程様式の標準化(OBS-20260725-01 watch 継続)

## 検証(2026-07-26・受入基準=起票時凍結分)

- **V1(陽性対照・回帰)**: fresh scaffold の full qualification 全 17 項目 PASS(IQ-01〜07・
  POS・N1〜**N8**・DET 2 回一致)— 既存 7 対照は改修後も判定不変・新負例 N7(E04 実 Git)・
  N8(E07 実 Git)追加。
- **V2(負例 6 種)**: (a) --runs 1 で full → argparse 拒否・--runs 0 → 拒否 /
  (b) 外部 `…/bomdd/hooks` へ hooksPath(絶対パス)→ **IQ-03 FAIL**(正準比較)/
  (c) hook の起動行コメントアウト → **IQ-02 FAIL**(非コメント行の構造検査)/
  (d) 不完全既存設備(profile のみ残存)+--skills-only → **exit 1**+欠落列挙・復旧手順 /
  (e) git user なし環境の scaffold → **bomdd-init exit 1**(REV-06 の致命化)/
  (f) GIT_DIR/GIT_WORK_TREE を外部リポへ向けた full qualification → **17 PASS・外部リポ
  HEAD/worktree 完全不変**(隔離実測)。
- **V3(回帰)**: self-conformance 全 PASS — C11 は構造化 JSON 判定(IQ-03 pass==false)+
  2 回決定性の回帰固定へ更新(所要 79s — 受入どおりの増分・CI 許容と判断)。
- **正直記載(製造中に検出・是正した欠陥 2 件)**: (a) IQ-02 初版の構造検査が実 hook の変数経由
  起動(`v=…` と `exec … --mode …` が別行)に不整合で scaffold を誤 FAIL — 2 トークン検査へ是正
  (fail-closed 側の誤りが初回実行で即顕在化= OBS-20260726-03 の 2 例目)。
  (b) **REV-12 の第二面**: sandbox git の隔離だけでは不足 — validator 子プロセスが汚染 env を
  継承し、外部リポの履歴で E06/E07 を判定(POS FAIL・N8 素通りとして (f) プローブが検出)→
  runner 起動時に自プロセス環境から GIT_* リダイレクト系を除去(hook 文脈は対象外の理由を
  コード注記)。検証手順側の学びとして、installed copy は凍結コピーであり template 修正は
  再設置まで波及しない(ECO-004 設計どおり)ことを再確認 — (f) 初回の偽 FAIL は stale runner。
- 影響なし予測: 的中(diff は 3 参照+台帳系のみ)。意図的挙動変更(git なし環境 exit 1)は
  (e) で実測どおり。

## 教訓(還元候補 — lesson-promote 経由)

- **隔離は「自分が起動する全子プロセス」まで閉じて初めて隔離** — sandbox の git だけ環境を
  浄化しても、検査器(validator)の subprocess が汚染 env を継承すれば判定が外部状態に依存する。
  隔離の受入は「汚染 env 下での全経路実測」で行う(V2(f) が第二面を実際に検出した)。

## 効果測定(宿題)

- 是正後の再独立検査(ECO-016 と合同・fresh 検査官)で runner/init 系所見 0 件になるか
- EXP-20260725-03 の実測時に line readiness の判定が新精度(正準比較・構造化判定)で走るか
