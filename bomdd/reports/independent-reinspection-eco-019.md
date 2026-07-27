# ECO-019 是正後 独立受入検査 — 第4ラウンド

対象 HEAD: `15b51637f2b8`

判定: **REJECT / 製造前凍結不可**

任務Aの5件はすべて **CLOSED**。ただし、宣言済み境界に帰着しない新規欠陥を5件(high 2、medium 2、low 1)確認した。

## 1. 任務A 判定表

| 所見 | 判定 | 実測した再現条件・結果 | 該当箇所 |
|---|---|---|---|
| IA-01 — E10 が pass-through hook を設備完全と判定 | **CLOSED** | 両hookを `#!/bin/sh; exit 0` としてメモリ上で再現。E10単独は依然 `[]` だが、新設E11が両hookを `equipment-neutralized` として検出した。存在と有効性を別reason codeへ分離した補償閉鎖。 | [process-validator.py:576](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:576)、[process-validator.py:588](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:588)、[process-validator.py:602](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:602) |
| IA-04 — legacy ECOのpost-cutoff証拠要求までID単位で免除 | **CLOSED** | cutoff前から `ECO-L=staged`、cutoff後にtrailerなしで`applied`を再現。`required={('ECO-L','applied')}`となり、E06を返した。導入点で到達済みのstagedだけが免除され、導入後遷移は免除されない。 | [process-validator.py:425](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:425)、[process-validator.py:438](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:438)、[process-validator.py:638](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:638) |
| IA-05 — merge証拠採用のみ第1親比較 | **CLOSED** | 第1親staged、第2親applied、merge結果applied、mergeにaccept trailerを再投入。mergeの合算baseはappliedとなり、merge trailerは`linked`へ採用されなかった。第2親のtrailer欠落に対してE06が残った。 | [process-validator.py:411](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:411)、[process-validator.py:430](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:430)、[process-validator.py:483](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:483) |
| 保護パス変更の履歴検査の不在 | **CLOSED** | cutoff後の保護パス変更commitについて、親状態にopen ECOがない条件を再現。`[E01] ... history:<sha>`を返した。走査は`--full-history cutoff..HEAD`。 | [process-validator.py:447](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:447) |
| NEW-01 — 両hook同時置換でE08/E10とも不発、無音PASS | **CLOSED** | 両hookを同時にpass-through stubへ置換。E08は置換済みhook自身からは発火せず、E10もファイル存在により空だったが、validateのE11が両hookを検出したため無音PASSは不成立。 | [process-validator.py:602](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:602)、[process-validator.py:762](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:762) |

## 2. 任務B 新規所見

### ECO019-IA-01 — high — 解析不能な履歴台帳を除外するとID削除を洗浄できる

- 再現条件:
  1. cutoff後に`ECO-X=staged`を追加。
  2. 次commitで台帳を不正YAML `changes: [` にする。
  3. その次で正常な`changes: []`へ復旧する。
  4. hookは`--no-verify`で回避し、validateを実行。
- 実測結果: 不正commitにはwarnが出るが、再演対象から除外された。復旧commitは空の親状態との比較となり、`violations=[]`。現在台帳にECO-XがないためE06/E09も発火せず、削除されたIDを受理できる。
- 該当行: [process-validator.py:399](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:399)、[process-validator.py:427](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:427)、[process-validator.py:432](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:432)
- 是正提案: replay範囲で変更された台帳が1件でも解析不能ならexit 2。履歴台帳の欠落と解析不能を空台帳から区別し、恒久負例へ「不正化→正常化によるID削除」を追加する。

### ECO019-IA-02 — high — dirty worktreeでHEADの証拠欠落を隠せる

- 再現条件:
  1. HEAD履歴で`staged→applied`をtrailerなしでcommit。
  2. commitせず作業ツリーの台帳だけstagedへ戻す。
  3. validateを実行。
- 実測結果: 同じ履歴にHEAD版appliedを与えるとE06。作業ツリー版stagedを与えるとE06は`[]`。履歴再演はHEADを走査する一方、現在状態は作業ツリーファイルから読むため、`required={('ECO-W','applied')}`があっても現在stagedなら証拠検査が行われない。
- 該当行: [process-validator.py:638](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:638)、[process-validator.py:746](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:746)、[process-qualification.py:173](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-qualification.py:173)、[process-qualification.py:246](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-qualification.py:246)
- 是正提案: validateの現在台帳・設備検査はHEAD blobを正本にするか、台帳・設備にHEADとの差分があれば測定不能にする。設置直後の未コミット状態は明示的なinstallationモードとして分離する。

### ECO019-IA-03 — medium — 保護パス履歴走査のGit失敗がfail-open

- 再現条件: 保護パス用`git rev-list --full-history`をreturn code 128として応答させる。
- 実測結果: 履歴保護パス違反はゼロ。例外・exit 2にならず、その面だけ無言で省略された。同様にcutoff検出の`git log`、親取得の`git log -1`にも未確認return codeがある。
- 該当行: [process-validator.py:370](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:370)、[process-validator.py:430](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:430)、[process-validator.py:449](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-validator.py:449)
- 是正提案: 履歴判定に使う全Git subprocessの非0をexit 2にする。空結果と実行失敗を構造的に分離する。

### ECO019-IA-04 — medium — qualificationがprofileの差分注入に追随しない

- 再現条件: profileを`register: meta/custom-register.yaml`、`initial: queued`、accept trailerを`X-Accept`へ変更。
- 実測結果: read-only関数プローブでもqualificationは`REGISTER=bomdd/60-change-register.yaml`、生成状態はstaged、OQ trailerは`BomDD-ECO-Accept`のまま。validatorが読むprofileとOQが操作する対象が分岐し、正当なadapt済み設備を誤って不適格にする。
- 該当行: [process-qualification.py:62](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-qualification.py:62)、[process-qualification.py:164](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-qualification.py:164)、[process-qualification.py:200](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-qualification.py:200)、[process-qualification.py:341](C:/Users/akira/source/repos/BomDD/method/templates/process-core/tools/process-qualification.py:341)
- 是正提案: installed profileを一度厳格ロードし、register・initial・states・trailer名を全OQ対照の単一入力にする。

### ECO019-IA-05 — low — product/CAD同名指定を事前拒否しない

- 再現条件: `bomdd-init Same --gui --cad-name Same`。
- 実測結果: path計算で`product_root == cad_root`、対象2件に対するunique pathは1件。存在事前検査は同じ未作成パスを2回検査して通過し、product scaffold後にCAD scaffoldを同じ場所へ重ねる。後段は失敗側になるが、不整合な生成残骸を残す。
- 該当行: [bomdd-init.py:363](C:/Users/akira/source/repos/BomDD/method/tools/bomdd-init.py:363)、[bomdd-init.py:368](C:/Users/akira/source/repos/BomDD/method/tools/bomdd-init.py:368)、[bomdd-init.py:384](C:/Users/akira/source/repos/BomDD/method/tools/bomdd-init.py:384)
- 是正提案: resolved/case-normalized pathでproductとCADの非同一性を生成前に強制する。

## 3. BOUNDARY-DUP

以下は新規所見数に含めない。

| 分類 | 条件 | 帰着理由 |
|---|---|---|
| BOUNDARY-DUP-01 | `history_replay_since`を違反後へ移動 | 適用範囲cutoffをcommit権限者が変更できるというIA-02の宣言済み境界そのもの。 |
| BOUNDARY-DUP-02 | states/trailersを変更して過去の合法性を再定義 | HEAD profileが規則を遡及定義するIA-03の宣言済み境界そのもの。 |
| BOUNDARY-DUP-03 | 履歴書換えでprofile初出点を移動 | NEW-03として申告された、リポ内履歴を自己アンカーできない系。 |
| BOUNDARY-DUP-04 | hookへvalidator文字列と`--mode`のdecoyを置き、実際は`exit 0` | 実測ではE11が`[]`になったが、実行体hookをcommit権限者が書き換えられるという同一境界へ帰着するため新規計上しない。 |

## 4. 総合判定

**REJECT**

- 任務A: **5/5 CLOSED**
- 任務B: 境界外の新規所見 **5件(high 2 / medium 2 / low 1)**
- BOUNDARY-DUP: 4分類、所見数には不算入

特に、解析不能な履歴台帳によるID削除洗浄と、dirty worktreeによるHEAD証拠欠落の隠蔽は、第2層validateが不適合履歴をexit 0へ落とし得るため受入不能。

read-only制約のためfull OQは実行していない。validator selftestは書込み不要部分44項目がPASSした後、一時ディレクトリを作成できず中断した。追加判定はファイルを書かないGit応答モック・純関数プローブ・コード読解で実施した。Python 3ファイルはAST parse成功、両hookは`sh -n`成功。

## 5. 遵守申告

- `bomdd/60-change-order-eco-019.md`〜`eco-023.md`の各「検証」節は読んでいない。
- `bomdd/60-change-register.yaml`の`verification`欄は読んでいない。
- リポジトリへの書込み・変更は行っていない。
- 最終`git status --short`は空。worktree/indexのdiffもともに空。
- 最終HEAD: `15b51637f2b8`

実応答モデル名: `GPT-5 (Codex)`  
セッション識別子: `019fa3fc-9f6f-7613-ba2c-11f9c79d97e5`

Codex session ID: 019fa3fc-9f6f-7613-ba2c-11f9c79d97e5
Resume in Codex: codex resume 019fa3fc-9f6f-7613-ba2c-11f9c79d97e5

---

## 真正判定(当方検証・2026-07-27 — 検査官出力の後付け注記)

実プローブ 4 件(fresh scaffold・実 git・実 validate/qualification)+コード読解 2 件で全数検証。
**裁定: 提起 5 件(ECO019-IA-01〜05)全件 CONFIRMED・誤検出 0**。通算(13+7+5+5)=
**30 提起・30 CONFIRMED**。任務A の 5/5 CLOSED は ECO-019 検証 V2 の当方プローブと一致(相互裏取り)。

### 実プローブの結果

- **P1(IA-01)= CONFIRMED**: staged 追加 → 台帳を `changes: [` へ不正化 → `changes: []` へ復旧
  (全 commit --no-verify)→ `validate OK(0 entries)`・exit 0。warn 表示のみで ECO-X の削除が
  受理された。**対照 P1b が重要**: 破損を挟まない素の削除は
  `[E03] ECO-X が台帳から削除された` で遮断される(exit 1)— つまり削除検査は存在し、
  **不正化→復旧はその検査のバイパス**として成立している(親比較チェーンの切断)。
- **P2(IA-02)= CONFIRMED・報告より軽い操作で成立**: HEAD に trailer なし applied → validate は
  E06(exit 1)。**worktree の台帳を staged へ書き戻すだけ(git add 不要)**で
  `validate OK(1 entries・証拠要求 2 遷移)`・exit 0。index へ stage しても同じ。履歴再演は
  HEAD を走査し required を正しく算出しているのに、E06 の突合先(現在 entries)が
  worktree/index から来るため隠蔽が成立する。
- **P4(IA-04)= CONFIRMED・実運用相当の実測**: 正当に adapt した設備(profile の register を
  `bomdd/custom-register.yaml` へ変更・git mv・validator 自体は本体リポで validate OK)で
  full qualification を実行 → **FAIL — 製造を開始しない**。発現は三態の混在:
  誤 FAIL(IQ-06/IQ-08/POS/POS4)+**負例の想定外通過**(N2/N3/N4/N7 が exit 0)+
  理由不一致の測定不能(N5/N8 が exit 2「台帳がない」)+DET 不一致。sandbox は installed
  profile を複写するのに、台帳の設置・遷移操作・trailer 付与はハードコード既定
  (`REGISTER`・`_reg_text`・`BomDD-ECO-Accept`)のため。**ECO-021(保護パスプローブの
  既定値前提)と同族 — OBS-20260727-16 の 2 例目に相当**(ECO-021 は protected_paths のみ導出化し、
  register/initial/trailers が残った)。
- **P5(IA-05)= CONFIRMED(限定つき)**: `Same --gui --cad-name Same` → 最終 exit は 1
  (fail-closed 側)だが**事前拒否がなく**、product git init 失敗を宣言した後も処理が続行し、
  同一ディレクトリへ product+CAD が重なった生成残骸(AGENTS.md「既存のため保持」= CAD パスが
  product 生成物を既存と誤認)を残す。検査官の「後段は失敗側になるが不整合な生成残骸を残す」
  記述と一致。

### コード読解の結果

- **IA-03(fail-open 非対称)= CONFIRMED**: 台帳再演の rev-list 失敗は
  `die(exit 2・測定不能)` へ倒すのに、保護パス履歴走査は `if pp.returncode == 0:` で
  **失敗時に無言でその面だけ省略**(else なし)。親取得 `log -1 --format=%P` の失敗も
  `parents=[]` へ縮退し base={} として続行する。同一ファイル内で測定不能の扱いが面ごとに
  分岐している(fail-closed 統一の残り)。
- **BOUNDARY-DUP-04(E11 decoy)= 実測再現+分類妥当の裁定**: decoy hook(`exit 0` 先行+
  validator 参照行と `--mode` 行を後置)を実 commit → validate OK・E11 不発を当方 P3 でも再現。
  `hook_invokes_validator()` は非コメント行の構造 grep であり、到達可能性を見ない。ただし
  リポ内の構造検査をいくら強化しても偽装との軍拡競争になる — 「実行体は commit 権限者が
  書き換え可能(監査可能だが阻止不能)」の宣言済み境界へ帰着するという検査官の分類は**妥当**
  (E11 の到達目標は素朴な無力化の検出まで — 境界文書への 1 行追記は次 ECO の裁定点)。

### EXP-20260727-06 の測定結果(本ラウンドの主目的)

**宣言済み境界の受理 = 成立(初測定)**。
- BOUNDARY-DUP 4 分類はすべて正しく境界へ帰着(当方裁定で誤帰着 0 — DUP-04 も上記のとおり妥当)。
- IA-02(cutoff 前送り)・IA-03(遡及適用)・NEW-03(履歴書換え)が**新規所見として再提起される
  ことはなかった**(検査官はこれらの変形を実測した上で自ら境界へ分類した)。
- 境界外の新規 5 件は全件 CONFIRMED — 境界受理が**新規欠陥の検出力を落としていない**
  (受理と検出の両立)。
- 測定上の設計注記: 受理の操作的定義は「BOUNDARY-DUP 分類の正使用」(申告+分類枠の付与)。
  帰着判定自体は検査官が行うため、申告が測定を無効化しない。

### 限界

検査官は N=1 ベンダー(GPT 系・自己申告モデル名 `GPT-5 (Codex)` — 過去 3 ラウンドの
`gpt-5.6-sol` と表記が異なる点は自己申告のまま記録)。read-only 制約により検査官側は
full OQ 未実行(当方 P4 で補完)。真正判定は当方(製造者側)の実プローブに依拠 —
第三者による再判定は未実施。

処置= ECO-024 起票(在庫可能分 5 件+E11 境界追記の裁定点)・gate ① 待ち。
