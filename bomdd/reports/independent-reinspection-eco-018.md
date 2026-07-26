## 1. 任務A 判定表

| 所見 | 判定 | 実測した再現条件・結果 | 該当箇所 |
|---|---|---|---|
| NEW-01 | **STILL-OPEN** | 単独hook削除・両hook削除・リネームは、validatorが起動すればE08、欠落状態ではvalidateがE10を返した。一方、両hookを `#!/bin/sh; exit 0` 相当に**置換してパスだけ残す**と、E10は空リストを返した。qualificationの構造検査は置換を不適合と判定するが、通常validateは呼ばない。したがって両hook同時置換ではE08を起動せず、validateも無音PASS可能。実Git commitは環境制約により未実施。 | [process-validator.py:480](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:480)、[process-validator.py:538](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:538)、[process-qualification.py:126](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-qualification.py:126)、[process-qualification.py:419](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-qualification.py:419) |
| NEW-02 | **CLOSED** | `open_states`、`protected_paths`、`states`順序、`trailers`、`history_replay_since` の有効なworktree変異を個別投入。全5件で返されたprofileはHEAD版と一致し、観測されたGit呼出しも `show HEAD:bomdd/process-profile.yaml` のみ。index版を読む経路はなかった。`initial`・`register` の個別変異と実Git stagingは未検証。 | [process-validator.py:174](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:174)、[process-validator.py:645](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:645) |
| NEW-03 | **STILL-OPEN** | cutoff内のborn-appliedは `[E02] history:A`、3状態飛越しは `[E03] history:A` を返し、違法commitのtrailerもlinked証拠から除外された。しかし、① `history_replay_since` を違法commit後へ進めた履歴、②履歴書換え後の最初のprofile追加点を違法commit後にした履歴は、ともに `violations=[] / scoped=[]`。さらに、当時3状態だった `staged→applied` を後続HEAD profileで2状態へ変更すると、同じ履歴がE03/E06ゼロになった。 | [process-profile.yaml:42](C:/Users/akira/source/repos/BomDD/method/templates/process-core/process-profile.yaml:42)、[process-validator.py:357](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:357)、[process-validator.py:403](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:403)、[process-validator.py:645](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:645) |

`--no-verify`・amend・rebase・cherry-pickについては、「違法commitがcutoff内の到達可能履歴に残る」結果グラフでの検出を確認した。各Gitコマンドを使ったend-to-end実行は未検証。force-push相当は、cutoffを後方へ移した結果グラフのみ実行した。

## 2. 任務B 所見一覧

### ECO018-IA-01 — high — E10がhook置換を設備完全と判定

- 再現条件: `CORE_EQUIPMENT` 全パスを存在扱いにし、両hookの内容をpass-throughへ置換。
- 実測結果: `check_equipment_complete()` は `[]`。同じ置換をqualificationの `_hook_invokes_validator()` に渡すと両hookとも `false`。
- 該当行: [process-validator.py:91](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:91)、[process-validator.py:543](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:543)、[process-qualification.py:95](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-qualification.py:95)
- 是正提案: validate側で設備変更履歴についてE08を再演する。少なくともhookを通常ファイルとして検査し、validator起動構造も検証する。qualificationのN12/N13へ片方・両方の置換、rename＋同名decoyを追加する。

### ECO018-IA-02 — high — cutoffを前送りすると履歴再演と証拠要求を同時に消せる

- 再現条件: born-applied違反の後のcommit `B` を `history_replay_since` に設定。または履歴書換え後の自動検出結果を`B`とする。
- 実測結果: 両ケースとも `台帳変更 0 commit・証拠要求 0件`、`violations=[]`。
- 該当行: [process-validator.py:360](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:360)、[process-validator.py:366](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:366)、[process-validator.py:410](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:410)
- 是正提案: overrideは自動導入点と同一またはそれ以前への拡張だけを許可する。履歴書換え対策には、cutoff OIDをリポジトリ外のCI/branch-protection設定で固定する。

### ECO018-IA-03 — high — HEAD profileが過去の合法性を遡及的に再定義

- 再現条件: 当時のprofileを3状態として `staged→applied` を記録し、後続HEAD profileを2状態に変更。
- 実測結果: 3状態規則ではE03＋E06。2状態の現HEAD規則で同じ履歴を再演すると違反ゼロ。逆方向ではstates順序変更とtrailer改名により、以前の適法履歴へE03/E06を誤発報した。
- 該当行: [process-validator.py:405](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:405)、[process-validator.py:425](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:425)、[process-validator.py:437](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:437)、[process-validator.py:645](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:645)
- 是正提案: commitごとにその親で有効だったprofileを読み、遷移・trailer名を版付きで再演する。profile変更は「次commitから有効」とし、過去へ適用しない。

### ECO018-IA-04 — high — legacy ECOのpost-cutoff証拠要求まで除外

- 再現条件: profile導入前に `ECO-L=staged`、導入後に `applied` へ合法遷移するがaccept trailerを付けない。
- 実測結果: 遷移自体は合法、`scoped=[]` となりE06/E09対象から除外され、違反ゼロ。
- 該当行: [process-validator.py:416](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:416)、[process-validator.py:428](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:428)、[process-validator.py:687](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:687)
- 是正提案: ECO ID単位で全免除せず、cutoff前に既に到達していた状態だけを免除する。cutoff後に発生した各遷移はlegacy ECOでもE06/E09対象にする。

### ECO018-IA-05 — high — mergeの証拠判定だけ第1親を使い、偽の遷移証拠を採用

- 再現条件: 第1親はstaged、第2親は既にapplied、merge結果はapplied。第2親のapplied遷移にはtrailerなし、merge commitにaccept trailerを付与。
- 実測結果: 合法性再演の親合算ではmergeに遷移なし。一方、証拠採用は `M^`（第1親）との比較でmergeをapplied遷移と誤認し、`linked[accept,ECO-M]=M`。E06を含め違反ゼロ。
- 該当行: [process-validator.py:421](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:421)、[process-validator.py:424](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:424)、[process-validator.py:450](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:450)、[process-validator.py:453](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:453)
- 是正提案: replay時にcommitごとの合算済み親状態をキャッシュし、trailer証拠も同じbaseとの比較でのみ採用する。`sha^`による第1親限定比較を廃止する。

性能については実Gitベンチ未検証。selftest実行は44項目までPASSした後、read-only環境で一時ディレクトリを作れず中断したため、性能・qualification全体の完走結果は主張しない。

## 3. 総合判定

**REJECT**

NEW-02の同一commit自己再定義は閉じたが、NEW-01とNEW-03はSTILL-OPEN。加えて、証拠スコープとmerge親合算に承認証拠を無音で落とすhigh欠陥を確認した。

禁止されたECO-018「検証」節および変更台帳の`verification`欄は未読。リポジトリは変更しておらず、最終 `git status --short` は空、指定3ファイルのdiffも空だった。

実応答モデル名: `gpt-5.6-sol`  
セッション識別子: `019f9ee7-ad8c-7f01-b503-d5fa4b954936`

Codex session ID: 019f9ee7-ad8c-7f01-b503-d5fa4b954936
Resume in Codex: codex resume 019f9ee7-ad8c-7f01-b503-d5fa4b954936

---

## 真正判定(当方検証・2026-07-27 — 検査官出力の後付け注記)

実プローブ 4 件+コード読解 2 件で全数検証。**裁定: 提起 5 件(IA-01〜05)+任務 A の
STILL-OPEN 2 件 = 全件 CONFIRMED・誤検出 0**。通算(13+7+5)= **25 提起・25 CONFIRMED**。

### 実プローブの結果(fresh scaffold・実 git)

- **P-A2(IA-01/NEW-01)= CONFIRMED・報告より重い**: 両 hook を `#!/bin/sh; exit 0` へ**置換**
  (削除でなく)して commit → **E08 不発**(置換後の stub が実行されるため第 1 層が自分の
  無力化を見ない)・**E10 も不発**(ファイルは存在する)・validate OK。さらに続けて
  ECO なしの `src/evil.py` を commit → **これも素通りし validate OK**。
  = 第 2 層には**保護パス変更の履歴検査が無い**(台帳の遷移しか再演していない)。
- **P-B(IA-05)= CONFIRMED**: 第 1 親 staged・第 2 親 applied(trailer なし)・merge に accept
  trailer → `validate OK(証拠要求 1 件)`。**遷移していない merge が accept 証拠として採用**
  された(再演は親合算・証拠採用は `sha^` 第 1 親という**同一走査内の基準不一致**)。
- **P-C(IA-04)= CONFIRMED**: 導入前から staged の ECO-L を導入後に applied へ(trailer なし)
  → `証拠要求 0 件・validate OK`。scoped を「**ECO の初出**」で切ったため、legacy ECO の
  **導入後の遷移**まで免除された(正しい規則は「cutoff 前に到達済みの状態のみ免除」)。
- **P-A(参考)**: 台帳違反を伴う置換攻撃は E02+E06 で検出された — 第 2 層は**台帳面では機能
  している**(二層化の設計自体は有効)。破れているのは設備面と保護パス面。

### コード読解の結果

- **IA-02(cutoff 前送り)= CONFIRMED**: `history_replay_since` は HEAD profile 由来のため変更に
  E08(open ECO)が要るが、**通れば違反の再演と証拠要求を同時に消せる**。自動検出側も履歴書換えで
  移動する。
- **IA-03(HEAD profile の遡及適用)= CONFIRMED**: 再演は全 commit に**現 HEAD の規則**を当てる。
  states を 3→2 に変えると過去の飛び越しが合法化し、逆方向では過去の適法履歴に誤発報する。

### 構造的観測(本 ECO 系列の中心)

1. **E10 は自分が文書化した失敗型を再演した** — 「存在確認を完全性検査の代用にしない」は
   transfer-04 4 類型 (c)・silence §16(c) として**当方の方法論に明記済み**の観点である。
   その規則を書いた側が、新設した検査で同じ穴を作った(**規則の存在は適用を保証しない** —
   FINDINGS §10.6「刻印済み規約の再発」の harness 自己適用面での再現)。
2. **第 2 層は「検査規則が被検査物の中にある」限り自己完結しない** — profile(規則)・cutoff
   (適用範囲)・hooks(実行体)はいずれも commit 権限者が書き換えられる。IA-01〜03 は個別の
   バグでなく**この一点の系**である。真の閉鎖にはリポ外の信頼アンカー(CI 設定・branch
   protection・外部で固定した規則版と内容ハッシュ)が要る — 検査官の IA-02 是正提案と一致。
3. **在庫可能な機械的欠陥は 2 件**(IA-04 の scoped 規則・IA-05 の基準不一致)+ 対策で水準を
   上げられる 2 件(hook 内容検査・保護パスの履歴再演)。IA-02/03 は在庫化せず**境界として
   文書化**すべき性質。

処置= 次 ECO の起票裁定待ち(在庫可能分)+ 境界の文書化。
検査官= Codex 実応答モデル **gpt-5.6-sol**・セッション 019f9ee7-ad8c-7f01-b503-d5fa4b954936。
検査官自己申告の未実施部分(実 git end-to-end・性能・qualification 完走)は当方プローブで補完した。
