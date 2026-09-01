# Change Order — ECO-046(観測前 push の機械遮断 — self-conformance witness+pre-push hook・C18)

> 裁定: user 2026-09-01「ECO-046 を起票して製造まで進めて」— 昇格審査(converge 延長 1 周で
> 正規収束・軌跡 3→1→0→0)の収束採用。**ECO-025 §7 が予約した「ローカル検査結果の機械的
> 強制(pre-push hook 等)の要否は測定で判断」の、測定成立(2 再演)後の実施**。

## 担当設備(equipment)

- 製造: requested/resolved `claude-fable-5`・Claude Code(Claude Agent SDK)・来歴 **self-reported**

## gate ①(製造承認と裁定点の採択)

user 指示が gate ① を兼ねる。予告済み裁定点 3 点の採択(差し戻し可能):
①**witness の tree 束縛**= 一時 index への `git add -A`+`write-tree`(検査した worktree 内容へ
束縛。未追跡の非 ignore ファイル残存はミスマッチ= 意図された厳密さ — 限界 (3) に宣言)
②**設置検収= C18 新設**(hooksPath=bomdd/hooks+hook 実在+突合ロジックの存在。CI は
push しない環境につき `GITHUB_ACTIONS` で **NA 宣言** — ECO-045 の NA 思想の踏襲)
③**witness は fast tier の PASS に束縛**(AGENTS 規律 2 の単一入口と一致・--dotnet 層は CI が
毎 push 担保)。

## 0. 実測(起票根拠 — 昇格審査の収束内容)

- **同一設備・同一規則の 2 再演**: ECO-024(検査 exit を chain で潰す・潜伏 1 コミット/9 分)/
  ECO-045(先頭コマンドの成功で観測を置換・潜伏 1 push)— いずれも観測経路でなく**強制経路**。
- **統制の非対称 2/2**: upstream(散文規律)= 0/2・downstream(CI)= 2/2 — 「push 前防御は
  存在せず push 後防御だけが働いた」。
- **前例閾値との一致**: converge 非起動→C16・calibrate 非起動→C17 はいずれも実測 2 件で機械化。
- **ECO-025 整合(延長 round 4 の実測)**: §7 スコープ外「機械的強制(pre-push hook 等)…
  強制の要否は OBS-20260727-23 の後継と EXP-20260727-26 の測定で判断」— 禁止でなく**予約**。
  二重統治の不採用は process-core(lifecycle 統治・台帳語彙)についてであり、本件は
  **既存計器(self-conformance)の結線**。AGENTS 規律 4 の実文「非 0 なら push しない」が
  防御点= pre-push を確定(commit は禁じていない)。

## 1. 変更要求(製造対象)

- **witness writer**: self-conformance 全検査 PASS 時に `.git/bomdd-selfconf-witness`
  (untracked・clone に残らない)へ〈検査対象 tree hash / PASS〉を記録。防御用であり検査結果に
  影響させない(git 外は黙って省略 — pre-push 側が不在を遮断)。
- **`bomdd/hooks/pre-push`(新設・tracked)**: push 対象 tip ごとに `^{tree}` を witness と
  突合 — witness 不在・PASS 以外・tree 不一致を遮断(削除 push は対象外)。exit code 直結
  (表示コマンドを介さない — EXP-20260727-26 の処方)。
- **C18 新設**: 設置検収(gate ② のとおり)。
- **設置**: `git config core.hooksPath bomdd/hooks`(local 設定 — clone ごと。C18 が未設置を
  検出して処方を表示)。

## 2. 影響なし予測(反証可能・製造前に凍結)

- diff は self-conformance.py / bomdd/hooks/pre-push(新設)+台帳系+improvements
  (EXP-20260727-26 第 1 回観測の記帳)。既存 C1〜C17 判定不変。配布物(method/templates・
  bomdd-init)は diff ゼロ — 本件は **BomDD 自リポの結線**であり製品リポへは非配布
  (製品リポの同面は process-core が担う)。
- 意図的挙動変更= ローカル push が witness 突合を通る(CI・他リポ非影響)。
- C16 は本 order を required と判定する見込み — receipt 埋め込み済み。

## 3. 較正と受入(起票時凍結)

- **C18 対照 3 腕**: A= hooksPath 未設定 → FAIL(固有理由+処方)/ B= 設置後 → PASS /
  C= `GITHUB_ACTIONS` 下 → NA 宣言 PASS。
- **hook 対照(実 push・scratch bare remote)**: W1= witness 不在 → 遮断 / W2= 検査 PASS →
  commit → push → 成功(緑腕)/ W3= witness tree を偽値化 → 遮断(tree 不一致腕)/
  W4= witness 2 行目を FAIL 化 → 遮断(結果腕)。
- **受入**: V1= C18 3 腕+W 4 腕 / V2= 全検査 PASS(既存判定不変)+witness が実際に
  書かれる / V3= **origin への本 push 自体が hook を通る**(新設機構の初回実使用= 新設者)/
  V4= CI 緑(C18 は NA 経路)/ V5= diff 窓 / V6= 較正 receipt(二軸)。

## /converge receipt(昇格審査ループ — 起動経路: 人間裁定〔提言+延長 1 周+起票指示〕)

- **判定: 収束**(round 軌跡: 3→1→0→0 — 延長 1 周は人間裁定・2 周連続ゼロ成立)。
- 周回: round 1 = 3 件(pre-push full 実行はコスト過大 → witness 方式 / ECO-025 衝突の明示 /
  意図的回避は信頼境界外)/ round 2 = 1 件(witness 書式は設計 ECO の領分)/ round 3 = 0 /
  round 4(延長)= 0(ECO-025 §7 実文により衝突懸念が解消 — 判定を変える新規指摘なし)。
- 検証した主張: ECO-024/045 の機序= 各 order 実文 / ECO-025 §3 裁定 3・§7 の実文 /
  AGENTS 規律 4 実文 / C16・C17 の 2 例閾値= 各 ECO 記録 / BomDD の hook 現況(hooksPath
  未設定・.git/hooks 空)= git config 実測。
- 未収束事項: なし。

## 4. 製造と受入の実測(2026-09-01)

- diff 監査の窓: baseline `c2c2448`(起票直前 HEAD・起票+製造は同一窓)→ head は受入時に確定。
- witness writer・pre-push hook・C18 を §1 のとおり製造。C18 対照 3 腕を計器から実測
  (A= hooksPath 未設定 → FAIL・固有理由+処方 / B= 設置後 → PASS / C= GITHUB_ACTIONS 下 →
  NA 宣言 PASS)。設置(`core.hooksPath=bomdd/hooks`)実施。
- **W 対照(scratch bare remote への実 push)**: W1= witness 不在 → 遮断(処方つき)/
  W3= tree 偽値 → 遮断(両 hash を表示)/ W4= FAIL 化 → 遮断 — 3 腕とも固有理由で成立。
- **W2(緑腕)が計器欠陥 2 件を本 push 前に捕捉(較正の実効)**:
  1. **CRLF**: witness writer が `write_text` の改行変換で CRLF を書き、hook の `sed` 取得値に
     `\r` が混入(正常 push が偽遮断される)。是正= `newline="\n"` 明示+hook 側 `tr -d '\r'`
     の二重防御。
  2. **同送タグの偽遮断**: hook が push される全 ref を突合し、`push.followTags` で同送される
     歴史タグ(旧 commit の tree)が遮断された。是正= 突合対象を `refs/heads/*` に限定し、
     タグは限界 (5) として宣言(当時の検査対象であり witness は現 tree のみを覆う)。
  **緑腕なしなら両欠陥は本 push(初回実運用)で発覚し工程停止だった** — 「常に赤の計器と
  弁別する known-good」(calibrate Q2)の実利の実測。
- 是正後: 全検査緑・witness は LF で再生成(od 実測)。W1〜W4 の再実測は §5 に記録。

## 5. CI 実測(V4)+W 再実測(V1 後半)

- **W 再実測(fix2 後)= 4/4 成立**: W1(不在遮断)/ W3(tree 偽値遮断)/ W4(FAIL 化遮断)
  各 1 件の固有発火・**W2(正常)= 成功**(main+同送タグが push され偽遮断解消)。
- **V3= origin への本 push が hook の初回実運用を通過**(d9603fa — witness 一致・遮断なし。
  新設機構の初回実使用者= 新設者)。
- CI: run 33487446674 — **PASS**(completed/success・headSha d9603fa 照合済み)。
  **C18 の NA 経路が CI 環境で初走行し成立**(GITHUB_ACTIONS 下で NA 宣言 PASS)。

## 6. クローズ

- diff 監査の窓: baseline `c2c2448` → head `d9603fa`(**窓閉鎖**)。窓内は
  self-conformance.py / bomdd/hooks/pre-push(新設)/ improvements(EXP-20260727-26
  第 2 回観測)+台帳系のみ — 影響なし予測が的中。
- 受入: V1(C18 3 腕+W 4 腕 — fix2 後 4/4)/ V2(全検査緑・witness LF 生成)/
  V3(本 push 通過)/ V4(CI 緑・NA 経路)/ V5(窓)/ V6(較正 receipt・下記)成立。
- **これで「規則を知っているのに今適用することが保証されない」故障型への機械層が 3 本目**:
  C16(converge 非起動)・C17(calibrate 非起動)・C18+hook(観測前 push)— いずれも
  実測 2 件 → 機械化の同一経路。
- このクローズが支持しないもの: 意図的回避の防止(witness 改竄・hook 除去・hooksPath 解除 —
  信頼境界外・最終層は CI)/ タグ単独 push の被覆 / 製品リポへの展開(process-core の領分・
  別裁定)。

### V6 — 較正 receipt(/calibrate 自己適用 — trigger ③: 新計器。二軸)

- 査定した主張と判定:
  1. 「hook は観測前 push(うっかり型)を遮断する」— **observed / 適格**(W1/W3/W4 の
     固有遮断+本 push の正常通過 — 両腕成立)。
  2. 「known-good 緑腕は『常に赤』と弁別し、偽遮断を検出する」— **observed / 適格**
     (W2 が CRLF・同送タグの 2 欠陥を本番前に捕捉 — Q2 対設計の実利を自ら実証)。
  3. 「本機構で観測前 push の再演率が下がる」— **unknown(理由コード: 未実行 —
     EXP-20260727-13 の系列観測が測る)**。
- 検出した計器欠陥と帰属: 2 件(CRLF・同送タグ — いずれも W2 緑腕が捕捉・同弧内是正)。
- 検出力の限界: コード恒久宣言の 5 点+「W 対照は witness 側変異であり『検査後の worktree
  改変』の直接再現ではない(同一判定式の等価プローブ)」。
