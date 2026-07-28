# ECO-024 — 第 4R 独立検査の在庫可能分 5 件(台帳洗浄・dirty worktree 隠蔽・fail-open 残り・qualification の profile 非追随・同名衝突)

> 状態: **製造完了・検証済み(2026-07-27)**。gate ① 承認(裁定 4 点は推奨採択)・
> baseline= 起票コミット 90b1f63。
> 発見経緯: ECO-019 是正後の第 4 ラウンド独立検査(EXP-20260727-06 の測定を兼ねる・
> Codex fresh・read-only・情報遮断)。報告= bomdd/reports/independent-reinspection-eco-019.md。
> 検査官提起 5 件は当方実プローブで**全件 CONFIRMED・誤検出 0**(通算 30 提起 30 CONFIRMED)。
> 任務A(ECO-019 の是正 5 件)は **5/5 CLOSED** — 本 ECO は新規所見のみを扱う。

## 裁定(gate ① — 2026-07-27)

**製造承認(maintainer — 「製造承認します、裁定 4 点は推奨どおりで」)**: ①replay 範囲の台帳
解析不能は**即 exit 2**(部分継続で洗浄面を残さない)②validate の突合先は **HEAD 正本**
(pre-commit/commit-msg は index のまま — commit 対象の検査)③E11 は**境界 1 行追記のみ**
(到達可能性検査は追加しない — 軍拡競争に入らない)④IA-04 は**導出関数化+非既定構成対照 1 本**
(直積対照は作らない)。baseline= 起票コミット 90b1f63(是正開始直前)。

## 是正(2026-07-27)

1. **IA-01(台帳洗浄)**: `reg_at_strict()` を新設 — 再演範囲の台帳変更 commit が解析不能なら
   **die(exit 2・測定不能)**。「warn して続行」は親比較チェーンを切り、〈不正化 → 復旧〉で
   ID 削除(E03)を洗浄できていた。復旧は履歴書換えでなく前進 commit での宣言を要求する。
2. **IA-02(dirty 隠蔽)**: validate モードの現在台帳を `_validate_entries()` へ分離し
   **HEAD を正本**にした(再演と同一世界)。worktree/index が HEAD と異なる場合は scope 注記を
   出す(判定は HEAD 基準)。**履歴にはあるが HEAD にない**= 削除として die。台帳が履歴に
   一度も現れない場合(設置直後)だけ worktree へ縮退 — 明示注記つき。pre-commit/commit-msg は
   index のまま(commit 対象の検査 — 裁定 2)。
3. **IA-03(fail-open)**: 履歴判定に使う git 呼び出しの非 0 をすべて die(exit 2)へ統一 —
   保護パス走査 `rev-list`・親取得 `log -1`(再演内・保護パス内の両方)・導入点検出 `log
   --diff-filter=A`。空結果と実行失敗を構造分離した。
4. **IA-04(profile 非追随)**: `installed_spec()` を新設し、OQ が触れる**全項目**
   (register/states/initial/final/mid/trailers/probe)を installed profile から導出。
   OQ-00 を「対照仕様の導出」へ拡張(導出不能は明示 FAIL)。IQ-06 の台帳パスも導出化
   (既定ハードコードが adapt 済み設備を「台帳がない」と誤 FAIL させていた)。
   `REGISTER` 定数は `REGISTER_FALLBACK`(表示用)へ降格。
5. **IA-05(同名衝突)**: bomdd-init が product/CAD の正規化パス同一を**生成前に**拒否
   (残骸ゼロ)。
6. **境界の明文化**: process-profile.yaml「既知の限界」節へ E11 の到達目標(素朴な無力化まで・
   decoy は同じ境界)を追記(裁定 3)。
7. **恒久収載**: N19/N20/N20b/N21 を qualification へ・**C11b**(非既定構成 profile の全対照)を
   self-conformance へ(裁定 4 の「対照 1 本」)。

**製造中の設計確定(理由記録)**:

1. **DET 用の detail に実行ごとに変わる値(sha)を入れない** — N19 の失敗詳細に生の validator
   出力(sha 入り)を載せたところ、**失敗時に DET(2 回一致)まで巻き添えで崩れた**。判定・理由
   集合を比較する検査では、詳細も正規化する(exit code+マーカー有無へ)。
2. **C11b の fixture は入口参照も adapt に追随させる** — register を移動した初版 fixture が
   IQ-08 で FAIL した(AGENTS.md の参照が空ポインタ化)。**検査は正しく反応しており**、
   fixture 側を実運用の手当て(入口も直す)へ合わせた — 検査を緩めていない。

## 検証(2026-07-27・受入基準=起票時凍結分)

- **V1(全対照)**: fresh scaffold で full qualification **34 対照すべて PASS**(既存 30 +
  **N19/N20/N20b/N21**)・DET 2 回一致・`PASS — line ready`。既存対照の判定は不変(回帰)。
- **V2(第 4R 再現条件の直接プローブ)**: P1(不正化→復旧)= **exit 2**(洗浄不成立)/
  P2(HEAD applied・worktree 書き戻し)= **E06 維持**(index stage 版も同じ・scope 注記つき)/
  P5(同名指定)= **exit 1・生成物 0 件**(生成前拒否)。**3 件とも閉鎖**。
- **V3(非既定構成)**: self-conformance **C11b PASS** — register=`meta/custom-register.yaml`・
  initial=`queued`・states=`[queued, applied]`・trailers=`X-Fix/X-Accept`・protected=`app/` の
  adapt profile で**全対照 PASS**+2 回決定性一致(IA-04 の誤 FAIL 解消を実測)。
- **V4(回帰)**: self-conformance **全 PASS**(C1〜C11・C11b)。validator selftest 全 PASS。
- **V5(MoviePad 再適格 — 版ずれの実測・正直記載)**: 正本 runner を MoviePad へ当てると
  **N19/N20/N20b が FAIL**。原因は MoviePad の**設置済み validator が ECO-024 以前**であること
  (OQ は対象リポの installed assets を sandbox へ複写して実測するため)。MoviePad 自身の
  設置 runner には新規負例が無く、**MoviePad の line 判定は従来どおり ready**(欠陥ではなく
  版ずれ)。設備更新はスコープ外(手動 3 手順 — ECO-021 記録済み)・**EXP-20260727-19 の
  発火データ**として還元へ。runner 側 docstring に「版の対」を明記した。
- **影響なし予測の検証**: **部分不的中(正直記載)** — 予測に `method/tools/self-conformance.py`
  が入っていなかった。裁定 4 の「非既定構成対照 1 本」を C11b として self-conformance へ置いた
  ため(製造中の置き場決定)。それ以外は予測どおり(validator/qualification/bomdd-init/
  process-profile.yaml+台帳系のみ・scaffold 経路の生成物は文言以外不変)。
- **CI 実測(2026-07-27)**: fix `dc97786` = **赤**(run 30291145716 — 両 OS とも
  `[C3] FAIL … ECO-024: diff 窓が開いている(head 未設定)`。**ローカルで検出済みの同一 1 件のみ**・
  他の失敗なし)→ accept `1535b5a` = **緑**(run 30291806295)。潜伏は **1 コミット・約 9 分・
  同一 ECO 内**で是正(基準線 11 コミット・約 2 日・5 ECO)。**EXP-20260727-13 の「潜伏 0 推移」は
  本 ECO で破れた**(逸脱 1 の直接の帰結)— 還元で正直に記録する。

### 製造中の手順逸脱 2 件(正直記載 — 是正済み)

1. **検査が赤のまま fix コミットが push された**(訂正版 — 初版の機械記述は誤りだった。下記「記録の訂正」)。

   **事実**: 検査実行と commit/push を**同一の実行要求**へ 2 行で投入した。1 行目
   `self-conformance > log 2>&1; echo "exit=$?"; tail -1 log` は `exit=1` と `FAILED` を**正しく
   出力**した。2 行目 `git add -A && git commit … && git push -q` は 1 行目と**条件で結ばれて
   おらず**、同一実行要求内で無条件に走った。実行要求は完了後にまとめて結果を返すため、
   出力を観測した時点では commit・push とも完了しリモートへ到達済みだった。
   不適合は C3(diff 窓が開いている= head 未設定)1 件で、CI も同一 1 件のみで赤になった
   (run 30291145716)。是正= 次コミット(accept `1535b5a`)で窓を閉じ C3 PASS・CI 緑を実測。

   **原因**: (a) 検査所要(3〜9 分)の往復を惜しみ、**結果を観測する前に後続操作を確定**した
   (b) 直前に同一ツリーで検査を通しており PASS の事前確率を高く見積もった
   (c) 検査と commit を**独立**な操作と分類した(実際は依存)。

   **責任**: 無条件の連続実行を書いたのは当方である。観測と実行の間に介入窓が無かったこと自体が
   その構成の結果であり、免責事由にならない。**「失敗を認識して進めた」のではなく
   「認識前に後続操作を確定した」**。

   **残余リスク**: ローカル検査結果の機械的強制は**未導入**。同種の再発は明文化では止まらない
   (今回止めたのは第 2 層の CI であって規範ではない)。強制の要否と手段は別途判断する。

   **記録の訂正(2026-07-28)**: 初版は「`echo` の成功が chain を通した」と記述したが誤り。
   実際には検査結果は正しく出力されており、**commit を制御するゲートが存在しなかった**。
   4 段階(規則存在/実行/伝送/操作の制御)では **③は健全・④が破れた**(結果が消費される前に
   後続操作が実行された)。
2. **台帳の書き戻しで全行が CRLF 化した**: Python の text mode 書き込み(`write_text`)が
   Windows で改行変換し、**台帳 756 行すべてが差分**になった(内容は 1 エントリ追加のみ)。
   是正= バイト単位で LF へ正規化し、実質差分が ECO-024 エントリのみであることを確認。
   一般形= **正本ファイルの機械書き換えは改行を保存する**(`newline="\n"` またはバイト I/O)—
   さもないと diff 監査(R-052/窓)が意味を失い、レビューが不能になる。

## 起票(2026-07-27)

### 事実(実測 — 真正判定プローブ・報告の後付け注記に全ログ)

1. **IA-01(high)— 台帳の不正化→復旧で ID 削除を洗浄できる**: replay は解析不能 commit を
   warn のみで対象外にし(`reg_at → None → continue`)、復旧 commit は親台帳 None → base={} で
   比較されるため、素の削除なら `[E03] 台帳から削除された` で遮断される操作が、間に不正 YAML
   commit を挟むと `validate OK(0 entries)` になる(P1/P1b 対照で実測)。
2. **IA-02(high)— worktree の台帳書き戻しで HEAD の証拠欠落を隠せる**: 履歴再演は HEAD を
   走査し required を正しく算出するのに、E06 の突合先(現在 entries)は worktree/index から
   読むため、HEAD が trailer なし applied でも**worktree を staged へ書き戻すだけ(add 不要)**で
   validate OK(P2 実測)。
3. **IA-03(medium)— 保護パス履歴走査の git 失敗が fail-open**: 台帳再演の rev-list 失敗は
   die(exit 2)なのに、保護パス走査は `if pp.returncode == 0:`(else なし)で失敗時に
   その面だけ無言省略。親取得 `log -1` の失敗も `parents=[]` へ縮退(コード読解)。
   同一ファイル内で測定不能の扱いが面ごとに分岐 — ECO-017 の fail-closed 統一の残り。
4. **IA-04(medium)— qualification が installed profile の差分注入に追随しない**: sandbox は
   installed profile を複写するのに、台帳設置・遷移・trailer 付与はハードコード既定
   (`REGISTER`・`_reg_text('staged')`・`BomDD-ECO-Accept`)。register パスを正当に adapt した
   設備(validator 自体は validate OK)で full qualification が **FAIL — 製造を開始しない**
   (P4 実測)。発現は ECO-021 と同じ三態(誤 FAIL= IQ-06/08/POS/POS4・負例素通り= N2/N3/N4/N7・
   理由不一致= N5/N8)+DET 不一致。**ECO-021 の同族 — 導出化が protected_paths のみで
   register/initial/trailers が残った(OBS-20260727-16 の 2 例目)**。
5. **IA-05(low)— product/CAD 同名指定を事前拒否しない**: `bomdd-init Same --gui
   --cad-name Same` → 最終 exit 1(fail-closed 側)だが事前拒否がなく、git init 失敗宣言後も
   続行して同一ディレクトリへ product+CAD の生成残骸を重ねる(CAD パスが product 生成物を
   「既存のため保持」と誤認)(P5 実測)。

### 観測(境界帰着 — 是正対象にしない)

- **BOUNDARY-DUP-04(E11 decoy)**: `exit 0` 先行+validator 参照行を後置した decoy hook は
  E11 を素通りする(P3 実測)。検査官・当方とも「実行体は commit 権限者が書き換え可能」の
  宣言済み境界へ帰着と裁定 — 構造検査の強化は偽装との軍拡競争になる。E11 の到達目標が
  「素朴な無力化の検出まで」であることの明文化は裁定点 3。

### 見逃しの構造

1. **例外経路の親状態が「空」へ縮退する**(IA-01/03 共通): 解析不能・git 失敗という測定不能
   事象が、fail-closed(die)でなく「空集合として続行」へ落ちる経路が残っていた。ECO-017 の
   fail-closed 統一は主経路を覆ったが、**replay 内部の縮退分岐**(reg_at None・parents 失敗・
   保護パス走査失敗)が被覆外だった — silence §16(a)(対象集合が空・不在・実行不能な場合に
   無音 PASS しないか)の replay 内部版。
2. **同一検査の入力が 2 つの世界(HEAD と worktree)から来る**(IA-02): required の算出は
   HEAD 世界・突合は worktree 世界 — 単一走査内の基準不一致(silence §16(e) の入力源版)。
3. **導出化の部分適用**(IA-04): ECO-021 は「既定値のハードコード禁止」を保護パスプローブに
   適用したが、同じ構造(profile 差分注入点 vs sandbox 既定)が register/initial/trailers に
   残った — 是正の閉包走査が「同型の全変数」まで及んでいなかった。

## 是正方針案(製造前・凍結前の草案)

1. **IA-01**: replay 範囲の台帳変更 commit が 1 件でも解析不能なら **die(exit 2・測定不能)**。
   「warn して続行」を廃止(過去に恒久不正 commit が残るリポは validate 不能になるが、それは
   fail-closed の正しい側 — 復旧には履歴修正でなく前進 commit での宣言を要求)。
2. **IA-02**: **validate モードの突合先を HEAD 台帳へ変更**(履歴再演と同一世界)。
   pre-commit/commit-msg モードは現行どおり index(commit 対象の検査 — 正しい設計)。
   worktree/index が HEAD と乖離している場合は validate が注記を出す(判定は HEAD 基準)。
3. **IA-03**: 履歴判定に使う **全 git subprocess の非 0 を die(exit 2)へ統一**
   (保護パス rev-list・親取得 log -1・cutoff 検出)。空結果と実行失敗を構造分離。
4. **IA-04**: sandbox の台帳パス・初期状態・trailer 名を **installed profile から導出する
   単一関数**へ(ECO-021 `_probe_rel` の一般化)。受入に**非既定構成対照**(register/initial/
   trailers を変えた adapt profile での full qualification 全 PASS)を追加。
5. **IA-05**: bomdd-init で product/CAD の **resolved path 同一を生成前に拒否**(残骸ゼロ)。
6. **境界文書の追記**: process-profile.yaml「既知の限界」節へ E11 の到達目標
   (素朴な無力化の検出まで — decoy は境界)を 1 行追記。

## 裁定を要する設計点(gate ①)

1. **IA-01 の die 範囲**: replay 範囲の解析不能 = 即 exit 2(推奨)vs 当該 commit のみ違反化。
   推奨理由= 「読めない台帳」は違反の有無を判定できない測定不能であり、部分継続は洗浄面を残す。
2. **IA-02 の突合先**: validate= HEAD 正本(推奨)vs 乖離検出で測定不能化。推奨理由=
   validate の意味論は「履歴と現在の合法性」であり、未コミット作業で結論が変わるべきでない。
3. **E11 境界追記**: 1 行追記のみ(推奨・軍拡競争に入らない)vs 到達可能性検査の追加。
4. **IA-04 の対照規模**: 導出関数化+非既定構成対照 1 本(推奨)vs 全変数の直積対照。

## 受入基準(事前登録 — 製造前に凍結する)

- **N19**(IA-01): staged 追加 → 台帳不正化 → 復旧(全 --no-verify)→ validate **exit 2**
  (測定不能・洗浄不成立)。素の削除は従来どおり E03(回帰)。
- **N20**(IA-02): HEAD に trailer なし applied・worktree を staged へ書き戻し → validate が
  **E06 を維持**(隠蔽不成立)。index stage 版も同結果。
- **N21**(IA-03): 保護パス走査の git 失敗注入(selftest モック)→ **exit 2**(無言省略しない)。
- **N22**(IA-04): register/initial/trailers を変えた adapt profile で full qualification
  **全 PASS**(誤 FAIL 解消)+既定 profile の全対照回帰不変。
- **IQ/初期**(IA-05): 同名指定 → 生成前拒否・**生成物ゼロ**(残骸なし)。
- 回帰: 既存全対照(30+ECO-023 分)PASS・DET 2 回一致・self-conformance 全 PASS・
  **push 後 CI 緑の実測**(ECO-020 規律)。
- 陽性対照の意味論: POS(正常 ECO 全経路)が全変更後も PASS。

## 影響分析(製造前予測 — 未凍結)

- 変更: `method/templates/process-core/tools/process-validator.py`(IA-01/02/03)・
  `method/templates/process-core/tools/process-qualification.py`(IA-04+N19〜N22)・
  `method/tools/bomdd-init.py`(IA-05)・`method/templates/process-core/process-profile.yaml`
  (限界節 1 行)。
- 正常運用への影響予測: (i) 解析不能履歴を持つリポは validate が exit 2 になる(意図的・
  fail-closed)(ii) validate の判定が未コミット編集に依存しなくなる(意図的)(iii) 既定
  profile の scaffold 判定は不変。既存製品リポへは kit 再設置まで非波及(ECO-004 設計)。

## スコープ外(明示)

- IA-02/03(cutoff 前送り・遡及適用)・BOUNDARY-DUP 系の是正(宣言済み境界 — リポ外アンカー
  系列 EXP-20260727-07 の守備範囲)。
- E11 の構造検査強化(裁定点 3 で追記のみ推奨)。
- 既設リポ(MoviePad)への一括再配布(更新は手動 — ECO-021 記録済みの経路)。
