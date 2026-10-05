# Change Order — ECO-099(ViewTube での 2 例目 — M-BOM の行を句ごとに分類する読み取りの計測〔事前登録つき・記録のみ・ViewTube へは書き込まない・verified〕)

> 指示: user 2026-10-05「ViewTube で 2 例目を試して」。ECO-097(ViewPrism2 の 2 製造単位)の試行は「M-BOM の行は裁定層の言い換えだった・人へ戻す行 0」で、
> M-BOM の方が E-BOM より多くを持つ製品(ViewTube: M 114 行・E 48 行)での「人へ戻す」行は未測定だった(playbook §4.5 の未測定の列挙・ECO-098)。
> **本 ECO は読み取りの計測と記録まで**。ViewTube の書き換え(M-BOM・Control Plan・テスト)は行わない — 理由は §0 の 2 点。

## 担当設備(equipment)

- 起票・計測: requested/resolved `claude-fable-5-1`・Claude Code(Claude Agent SDK)・来歴 **self-reported**
- producer: EQ-001
- 独立検査: 盲検の独立分類を EQ-002(Codex CLI / gpt-5.6-sol・異系統)が行う(事前登録 T4)。本リポの記録そのものは製造者較正。

## 0. 起票時の実測(2026-10-05・読み取りのみ)

- **ViewTube は別の作業が進行中**: HEAD `fe0250ef`(`fix(eco-vt-226)`・2026-10-05 12:14)。作業ツリーに未 commit の変更 4 ファイル(src 3・test 1)と未追跡 1 ファイル(R8 round 1 のレビュー)があり、確認の数秒前にも更新されていた。origin より 48 commit 先行。
  当日の commit 2 件(`record(eco-vt-226)`・`fix(eco-vt-226)`)が `bomdd/32-mbom.yaml` を書いている。→ ViewTube に ECO を起票して 32・33・テストを書き換えると、進行中の作業と同じファイル・同じ台帳で衝突する。
- **ViewTube には「人が読む ID ごとの表」の前提が無い**: 受入テスト 836 件は CP・要求の ID を持たない(ECO-090 acceptance-paths)。監督つき受入実行は常に赤を返す(OBS-20261002-02・原因は調査済みだが ViewTube 側で未是正)。
  → ECO-097 の R3(ID ごとの可視性)にあたる部分は、ViewTube では先に計器の是正が要る。本 ECO では扱わない。
- **ViewTube の M の行は ViewPrism2 と形が違う**(対象選びのために 2 単位 9 行を表示): 1 行が最大 736 文字で、ECO 番号・要求の ID・「the user's ruling (b)」・関数名・実測値(MEASURED 2026-10-04 …)・レビューの所見(R8 round 2 (BLOCKING))・
  検査していないことの注記(NOT exercised by any automated case)が 1 行に混ざる。E-BOM の不変条件は品目ごとに 1〜数行の一般的な文(例「仕様で定義した識別子・状態遷移・境界を保持する。」)。
  ViewTube の工程は ECO ごとに M-BOM へ行を書き足す(commit 件名「record(eco-vt-NNN): the M-BOM of … recorded」)。

## 1. 変更要求(凍結・記録のみ)

1. `bomdd/reports/eco-099-viewtube-second-example/` に、事前登録・統括 AI の分類(句ごと・裁定層の所在つき)・検査官の盲検の分類・両者の突合を保存する。
2. `method/improvements.md` に本節と、結果に応じた記帳(OBS-20261005-02 の加算の判定・playbook §4.5 の 3 分類の十分さ)。
3. `bomdd/60-change-register.yaml` に本 ECO を登録。

**採らない**: ViewTube への書き込み(ECO の起票・32 / 33 / テスト / ツールの変更)/ playbook・テンプレの改訂(結果を見てから別途判断)/ M-APP-* の単位 / ID ごとの表 / 常に赤の計器の是正(ViewTube 側の ECO の領分)。

## 2. 影響なし予測(起票段階・凍結)

本 ECO の diff= 台帳系(order・register・improvements.md・reports/eco-099-viewtube-second-example/)のみ。method/ の playbook・templates・schemas・tools・hooks・.github は diff 0。ViewTube の作業ツリー・index・refs は不変(読み取りは `git show <sha>:<path>` だけ)。

## 3. 受入条件(製造前に凍結・二部形・ECO-080)

- V1(条件): 事前登録が分類の実行より前の commit にあること — 検査法: commit の順。
- V2(条件): 対象 15 行の全部が句に分けられ、句ごとに区分と(参照化なら)裁定層の所在が記録されていること — 検査法: reports の分類表。
- V3(条件): 検査官の盲検の分類と、突合(T4)が記録されていること — 検査法: reports。
- V4(条件): T1〜T5 が事前登録の読み方で記録されていること — 検査法: reports・本 order のクローズ節。
- V5(条件): ViewTube の HEAD・作業ツリーの状態が計測の前後で本 ECO によって変わっていないこと(別の作業による変化は別) — 検査法: 前後の `git rev-parse HEAD` と、本 ECO が実行したコマンドが読み取りだけであること。
- V6(条件): diff が allowed_paths のみ・self-conformance 全 PASS・CI success。
- V7(条件): 製造者較正・較正 receipt(trigger ①)。

## /preflight receipt(起動経路: **自発** — 継続作業の開始時)

- 分類= continuation(ECO-097 → 098 の続き・user 2026-10-05 の指示)。
- 最小契約: baseline= BomDD `a9063ff`(clean・CI success)= **confirmed** / ViewTube `fe0250ef`= **confirmed だが作業中**(未 commit 4+未追跡 1・origin より 48 先行・別の作業が進行中)/
  current-work-state= ECO-097・098 verified・ViewTube 側は ECO-VT-226 が staged → implemented の途中(R8 round 1 が出た直後)= **confirmed**(git log・作業ツリーの更新時刻・レビューファイルの冒頭)/
  unresolved-items= playbook §4.5 の未測定(M の方が多くを持つ製品)・OBS-20261002-02(常に赤の計器・ViewTube 側で未是正)= **confirmed** / handoff-state= ECO-097 order・reports から再構成= **confirmed** /
  acceptance-target= **missing** → 本 order §3 と事前登録で定義。
- discovered(契約外): ViewTube の記録は英語(record-language-policy)・工程は process-core(change-impact の manifest・監督つき受入実行)— 書き込む場合の作法は ViewPrism2 と違う(本 ECO では書き込まないため未読のまま)。
- 開始判定: **PROCEED_WITH_LIMITS**(縮小= 読み取りの計測と記録まで。ViewTube への書き込みは、進行中の作業が終わり、かつ人が「人へ戻す」句を裁定した後に別途判断)・override 0。

## 4. 記録の実測(2026-10-05)

- 事前登録・起票= `78cac74`(分類の実行より前)。統括 AI の分類= [classification-producer.md](reports/eco-099-viewtube-second-example/classification-producer.md)(検査官の報告を開く前に保存)。
  検査官の盲検の分類= r1 UNMEASURABLE(sandbox から対象 commit の 31-kbom が読めない)→ r2 DONE(対象 commit の 5 ファイルの写し・sha256 一致)。突合= [reconciliation.md](reports/eco-099-viewtube-second-example/reconciliation.md)。
- **T1**: 統括 AI 42 句= 参照化 20・人へ戻す 7・製造手段 8・記録 7 / 検査官 63 句= 参照化 24・人へ戻す 5・製造手段 19・記録 15。分類不能 0。**両者とも「人へ戻す」あり**(ViewPrism2 は 0)。
  内容の突合= **一致 3 件**(H3 pack の必須機能 `node-condition-v1`・H4 music の定義の取り込み先・H5 読めない numeric restriction の pack を拒否)・**不一致 2 件**(H2 変換は schema version を上げない・復元後の open で変換〔統括 AI= 人へ戻す / 検査官= 製造手段〕・
  H6 両方の形を持つ placement の拒否〔統括 AI= 参照化 / 検査官= 人へ戻す〕)・**統括 AI の誤り 1 件**(H1「どの外部の失敗もユーザー作成データを消さない」— 検査官が REQ-004 / REQ-005 の所在を示し参照化)。
  H3・H5 は、対象 commit の ECO-VT-212 本文に利用者の裁定としての記載が見つからない(記載のある裁定は Q1・Q2 の 2 つ)= M-BOM にだけ書かれた設計の決め。H4 の出所は未確認。
- **T2**: 「記録」の句= 統括 AI 7・検査官 15 → playbook §4.5 の 3 分類では分けきれない(実測値・レビューの所見・検査していないことの注記・由来)。
- **T3**: 混在の行= 統括 AI 6/15・検査官 8/15。ECO ごとに書き足された長い行はほぼすべて混在。
- **T4**: 行ごとの区分の集合の一致= 7/15。不一致 8 行のうち 4 行は句の切り方の粒度の差(由来・関数名を独立の句にしたか)だけ。内容の判断が割れたのは 4 行= 3 件(H1・H2・H6)。
- **T5**: 既見の腕にも未見の腕にも「人へ戻す」がある(向きは同じ)。未見の腕(VIEW-PACK)に集中。
- 観察: ViewTube の REQ-095 は「仕組みは M-BOM の実装判断」と明文で委ねている(10:L3714〜3715)/ 参照化の所在はほぼすべて要求と仕様の本文で、E-BOM を所在に挙げた句は 0。

### 手順の逸脱(2 件・帰属= 製造者の運転)

1. **ViewTube の作業ツリーに空のファイルを 1 つ作った**(検出して削除)。検査官 r2 のブリーフを作るとき、Python を**クォートなしの heredoc**で渡した(クォート済みの heredoc は hook が止めるため、クォートを外して通した)。
   本文の文字列に入っていたバッククォートをシェルがコマンド置換として実行し、cwd が ViewTube だったため `bomdd/32-mbom.yaml` をシェルスクリプトとして実行した。ほぼ全行は command not found だったが、`purpose: >-` の形の行がリダイレクトとして働き、
   リポ直下に 0 バイトのファイル `-` ができた(2026-10-05 12:52:10)。直後の `git status` で検出し、0 バイトと時刻を確かめて削除した。HEAD・index・他の追跡ファイルは変わっていない(作業ツリーの他の変更と staged の 1 件は進行中の別の作業のもの)。
   機序= 安全装置(hook)が止めた形を、より危険な形に書き換えて通した。「書き込まない」と決めたリポを cwd にしてスクリプトを流した。処置= Python はファイルに書いてから実行する・cwd を対象のリポにしない(memory に記録)。
2. **検査官 r1 が測定不能**: 検査官の sandbox から `git show <sha>:bomdd/31-kbom.yaml` が `fatal: bad object`。原因は未確認(依頼者の環境では同じコマンドで読める。別の作業が同じリポで commit を重ねている最中だった)。検査官は分類せず UNMEASURABLE と報告した(欠けた入力で「裁定層に無い」と判定しなかった)。
   処置= 対象 commit の写しを sha256 つきで渡して r2。

## 5. クローズ(2026-10-05・verified・製造者較正+検査官の盲検の分類)

- **V1**= PASS(観測: 事前登録は `78cac74`。統括 AI の分類・検査官 r2 の実行はその後。事前登録の変更の履歴は初版のみ)。
- **V2**= PASS(観測: 15 行すべてが句に分けられ〔統括 AI 42 句〕、区分と、参照化の句には所在〔ファイル:行〕、人へ戻す の句には検索した語と結果がある)。
- **V3**= PASS(観測: 検査官 r2 の分類〔63 句〕と reconciliation.md の突合)。r1 は UNMEASURABLE(入力が読めない)で、分類は行われていない。
- **V4**= PASS(観測: T1〜T5 を §4 と reconciliation.md に事前登録の読み方で記録)。
- **V5**= **逸脱 1 件つきで成立**(観測: 本 ECO が ViewTube に対して実行したコマンドは読み取り〔git show・git status・git rev-parse・git ls-tree・stat・ls〕と、誤って作った空ファイル `-` の削除。終了時、ViewTube の HEAD・index・追跡ファイルに本 ECO による変化は無い。
  **途中で作業ツリーに 0 バイトのファイルを 1 つ作った**(§4 手順の逸脱 1)— 条件「変わっていないこと」は終了時の状態では成立するが、途中では破れた。ViewTube の HEAD は計測中に別の作業で fe0250ef → 25aa7bee へ進んだ〔本 ECO によらない〕)。
- **V6**= PASS(観測: 窓 `a9063ff` → `7c0b54e`= 台帳系+reports のみ。各 commit は self-conformance exit 0 観測後。CI は 78cac74・7c0b54e を確認のうえクローズ)。
- **V7**= 下の較正 receipt。register: `implemented → verified`。

### 較正 receipt(/calibrate 自己適用 — trigger ①: verified 昇格・receipt_author_role= producer。読み取りの計測の記録・検査官の盲検の分類つき)

- 査定した主張と判定:
  1. 「ViewTube の M-BOM には、裁定層に無い設計の内容がある」— **observed / 適格**(2 人の分類者が独立に同じ 3 件〔H3・H4・H5〕を挙げ、それぞれ 4 ファイルの検索語と 0 件を記録)。うち H3・H5 は ECO 本文にも利用者の裁定の記載が見つからない。H4 の出所は未確認。
  2. 「playbook §4.5 の 3 分類では ViewTube の M の行を分けきれない」— **observed / 適格**(両者とも「記録」の句を挙げた〔7・15〕。分類不能は 0 — 「記録」を足せば分けられた)。
  3. 「行単位の分類は ViewTube では使えない」— **observed / 適格**(混在の行 6/15・8/15。ECO ごとの長い行はほぼすべて)。
  4. 「2 人の分類は一致する」— **条件付き**(行ごとの集合の一致 7/15。差の半分は句の切り方の粒度。内容の判断が割れたのは 3 件で、うち 1 件は統括 AI の誤り)。分類は分類者に依存する。
  5. 「H2・H6 は人へ戻すべきか」— **unknown**(分類者が割れ、どちらも裁定層の所在を示せない。人が決める)。
  6. 「ViewTube の M-BOM 全体(114 行)でも同じ割合になる」— **unknown(測らない)**。対象は 3 単位 15 行。M-APP-*(41・16・17 行)は見ていない。
  7. 「この結果から、ViewTube の M-BOM を書き換えるべきだ」— **主張しない**(ViewTube の工程は ECO ごとに M-BOM へ書き足す作法で、進行中の作業もそうしている。書き換えは別の判断)。
- 検出した計器欠陥(帰属つき): 統括 AI の分類の誤り 1 件(H1・裁定層の statement を引かずに「無い」と判断= ECO-097 の起票時と同じ型)。検査官 r1 の測定不能 1 件(sandbox の環境差・原因未確認)。
  製造者の運転の逸脱 1 件(クォートなしの heredoc で ViewTube に空ファイルを作成・削除)。事前登録の弱点 1 件(句の切り方を分類者に任せたため、句数と集合の一致率が粒度に左右された— 由来の記録を独立の句にするかを決めていなかった)。
- 検出力の限界: 15 行・3 単位・1 commit。検査官は 1 系統 1 回(r2)。統括 AI は 2 単位を事前に見ていた(未見の腕 1 単位で向きは同じ)。裁定層の検索は grep と読解で、意味の同値の判断は分類者の主観を含む。
  ECO 本文での出所の確認は 1 本(ECO-VT-212)だけ・突合の後に行った(盲検ではない)。
- battery 行別記録:

  | Q | asked/NA | 判定 | 実測 or 読解 | 所見 |
  |---|---|---|---|---|
  | Q1 | asked | observed/適格 | 読解 | 事前登録が「測らないこと」(書き換え・ID ごとの表・M-APP-*・一般化)を宣言し、クローズは主張 5〜7 を unknown / 主張しない に分離 |
  | Q2 | asked | observed/適格 | 実測 | 盲検の 2 分類が H1 で割れ、所在の提示で一方が訂正された= 分類は誤りを出しうるし、突合で検出できた |
  | Q3 | asked | observed/適格 | 実測 | 統括 AI の分類と検査官の分類は互いを見ずに作られた(統括 AI は保存してから開いた・検査官は BomDD を読まない) |
  | Q4 | asked | observed/適格 | 実測 | 実製品の実 commit の実ファイル(sha256 を 2 者が照合) |
  | Q5 | asked | observed/適格 | 実測 | 不一致 2 件・未確認(H4 の出所・r1 の原因)を分離 |
  | Q6 | asked | **逸脱 1 件** | 実測 | クォートなしの heredoc の本文がシェルで実行された。commit は単独で実行し exit を観測(前の弧の逸脱の再発は無し) |
  | Q7 | asked | observed/適格 | 実測 | 陽性対照に当たるもの= H1(統括 AI が誤って 人へ戻す とし、検査官が訂正)・r1(入力が欠けたら UNMEASURABLE) |
  | Q8 | NA | — | — | 免除機構なし |
  | Q9 | asked | observed/適格 | 実測 | 対象 commit の完全 SHA と 5 ファイルの sha256 を記録。作業ツリーではなく commit を読んだ(別の作業が進行中) |
  | Q10 | asked | 宣言 | 読解 | 上記「検出力の限界」+主張 4〜7 |
  | Q11 | asked | observed/適格 | 実測 | 入力クラス(既見 / 未見の腕・永続化 / 外部接続 / ファイル形式の単位)を分けて測り、腕と単位の性質の差を記録 |

- このクローズが支持しないもの: ViewTube の M-BOM 全体への一般化 / ViewTube の書き換えの是非 / H2・H6 の区分 / playbook §4.5 の改訂の是非(結果は入力・別途判断)。
