---
name: handoff
description: AI→人間のハンドオフ・プロトコル。ターンを終えて人間へ制御を渡すメッセージごとに、interaction(INFORM/DECIDE/DISCUSS/REQUEST)と execution(CONTINUING/BLOCKED/COMPLETE/PAUSED)を先頭 1 行で宣言し、mode ごとの必須要素を満たしてから送る。人間が「報告か・質問か・議論か・AI は止まっているか」を逆推論しなくて済むようにする通信契約。長い報告・裁定要求・設計議論・完了報告・中断報告のすべてが対象。フリースタイル区間(形式なし)は人間の宣言でのみ開始・終了し、区間内でも裁定・依頼・タスク終了の 1 通は契約に戻る。
---

# /handoff — AI→人間の制御移譲プロトコル

> 出自: 2026-09-11 BomDD ECO-062 Phase 5 run-01 の報告に対する user 批評 —「裁定に必要な入力」と「実験報告」が混ざり、
> 人間の仕事が裁定でなく再分析になった(REPORT としては良いが RULING REQUEST として弱い)。改善は文章術ではなく
> **応答の型付け**で行う。本スキルは BomDD の方法論ではなく **ハーネス側の通信規約**(所在は `.claude/skills/` のみ・
> user 裁定 2026-09-11 1:A・product-profile 非接触・計測後に正本化を判断 → 2026-09-12 試行評価後の user 裁定 A= 採用・v0.3・
> AGENTS.md から参照〔ECO-070〕・配布〔product-profile〕は別 ECO)。
>
> 構造: **§1 契約(normative・小さく固定)**と **§2 実装規則(交換可能)**を分離する。契約は「何を宣言し何を含むか」だけを
> 決め、書き方・個数・順序は実装側に置く。モデルや用途が変わっても契約は変えない。

## 1. 契約(HANDOFF CONTRACT v0.4・normative)

> v0.1 → v0.2(2026-09-11・user DECIDE「A」): 第 4 の mode **REQUEST**(人間に作業を依頼し成果物を待つ)を追加。契機= run-02 の運転員依頼を INFORM で送り
> user が訂正(INFORM は人間のアクションなしの型)— EXP-20260911-01 の mode 訂正 1 件目。
>
> v0.2 → v0.3(2026-09-12・user DECIDE「A」・ECO-070): 試行評価(handoff 67・DECIDE 12/12 が reply_format どおり・mode 訂正 1・REQUEST の成果物回収に
> 追加 5 往復・INFORM/BLOCKED を FAIL H2 申告のまま 3 通送信・待機通知が 38/67)から 5 点+待機形を織り込む: ①ヘッダ組合せの許容表を契約に置き structural FAIL は
> 送信停止 ②DECIDE の options は各案同形の帰結(得る/失う/戻せるか)+非推奨案が劣る理由 ③独立項目は番号を分け部分採択可能に ④decision_question を先頭に
> ⑤REQUEST の deliverable は穴埋め様式。所在は変えず AGENTS.md から参照する。
>
> v0.3 → v0.4(2026-09-12・user AGREE・ECO-071): **フリースタイル区間**を契約に定義。①区間の開始と終了は人間の宣言のみ(既定は契約・AI の推定で形式を落とさない)
> ②区間内はヘッダも必須要素もなし ③片方向ラチェット= 区間内でも裁定・依頼・タスクのターン終了を含む 1 通はその通だけ契約に戻り「区間は継続」と明記する。
> 根拠= 誤分類のコストが非対称(タスク中に形式を落とすと再分析コストが戻る・会話中の形式はヘッダ 1 行)+「会話かタスクか」の推定はこの契約が不信を置いた判断と同種。

```text
HANDOFF CONTRACT v0.4

Scope:
  A handoff is the message that ends the AI's turn and returns control to the human.
  Intermediate progress lines within a turn are not handoffs.
  A turn that ends only to wait for a harness notification (background task,
  no human action, automatic resumption) is a handoff of mode INFORM / CONTINUING
  in the wait form: what is awaited and what depends on it, nothing else.

Free-style span:
  The contract applies by default. A free-style span begins and ends only by
  the human's declaration; inside it, messages carry no header and no required
  fields. The AI never enters a span by its own inference.
  One-way ratchet: if, inside a span, a message needs a decision, asks the
  human for work, or ends a task turn, that single message returns to the
  contract and says the span continues. Task -> conversation is the human's
  switch only; conversation -> task is automatic for that message.

Every handoff starts with:
  [INFORM|DECIDE|DISCUSS|REQUEST / CONTINUING|BLOCKED|COMPLETE|PAUSED]

Valid combinations (anything else is a structural FAIL and is not sent):
             CONTINUING  BLOCKED  COMPLETE  PAUSED
  INFORM        yes        no       yes      yes
  DECIDE        yes        yes      no       yes
  DISCUSS       yes        yes      no       yes
  REQUEST       yes        yes      no       no
  (INFORM never waits on the human, so INFORM/BLOCKED is invalid; a finished
   scope with a pending question is DECIDE/BLOCKED or /PAUSED, not /COMPLETE.)

Single mode:
  One handoff declares exactly one interaction mode.
  Content belonging to another mode goes to a separate handoff, or to an
  explicitly delimited appendix after the packet. The appendix must not
  contain questions or decisions.

INFORM requires:  information being handed off / human_action: none / execution state explanation
DECIDE requires:  decision_question / options, each with its consequence (gain, loss, reversibility) /
                  recommendation, including why the other options are worse / reply_format /
                  execution state explanation
                  Independently decidable items are numbered as separate decisions so each
                  can be adopted or rejected on its own.
DISCUSS requires: discussion_question / thesis / reasoning / counterpoint /
                  what_would_change_thesis / explicit non-decision status
REQUEST requires: request (what the human is asked to do) / deliverable, as a fill-in form the human
                  returns as is (every expected line with its fields) /
                  why_human (why the AI cannot do it itself) / execution state explanation
                  The reply to a REQUEST is the deliverable itself. INFORM never asks for human action.

Execution states:
  CONTINUING = the AI keeps working after this handoff
  BLOCKED    = an input or ruling required to proceed with the current request is missing
  COMPLETE   = the requested scope is finished (verified or explicitly not)
  PAUSED     = work is intentionally suspended, independent of whether it could proceed

Before sending:
  1. validate header combination against the table          (structural check)
  2. validate required fields exist                          (structural check)
  3. validate message purpose agrees with declared mode      (semantic self-check)
  4. validate single mode (no undeclared-mode content outside the appendix)
  5. rewrite if invalid. A structural FAIL is a hard stop: the handoff is not
     sent with a self-reported FAIL. Only an unresolved semantic self-check
     may be reported and sent.
```

契約が言わないこと: options の個数・reasoning の個数・行数・出現順・分類の手順・書き直し回数・DISCUSS の収束法。これらは §2。

## 2. 実装規則(交換可能・default)

### 2.1 分類(classify)— 決定木を上から当て、最初に yes になったところで決める

```text
Q0 人間にしかできない作業(私が代行できない・してはいけない)を頼み、その成果物を待つ必要があるか
     yes → REQUEST(成果物が返るまで BLOCKED。独立に進められる部分があれば CONTINUING で名指し)
Q1 私の次の行動が、人間にしか決められない選択で分岐するか
     yes → DECIDE。分岐に依存しない部分があれば CONTINUING(独立部分は進める・依存部分を名指し)、なければ BLOCKED
Q2 私に立場はあるが、コミットする前に人間の見解で変わりうる論点があるか
     yes → DISCUSS(execution は作業状態に従う。コミットを意図的に保留しているなら PAUSED)
Q3 それ以外 → INFORM(CONTINUING / COMPLETE / PAUSED のいずれか)
```

ガード: 慣例・コード・台帳で確かめられる判断を DECIDE にしない(自律の範囲)。逆に、人間の裁定事項を DISCUSS に逃がさない
(コミット回避の動機を疑う)。「〜しますか?」「必要なら言ってください」で終わる末尾付加は、隠れた DECIDE か隠れた DISCUSS —
本体に昇格させるか削る。

待機: ターンがハーネス通知待ち(バックグラウンド検査の完了など)だけで終わるなら、決定木を通さず INFORM/CONTINUING の**待機形**(§2.2)。

区間: フリースタイル区間内(§1・人間が宣言済み)では決定木を Q0/Q1 の検出にだけ使う — yes ならその 1 通は契約に戻り「区間は継続」と書く・no なら形式なし。
区間に入るのは人間の宣言だけ(「会話だと思ったので形式を落とした」は違反)。区間の終了も人間の宣言(タスク指示が来たら、それを終了宣言とみなしてよいが、その旨を最初の handoff に書く)。

### 2.2 生成(generate)— mode ごとの default

- 共通: パケット本体は 15 行程度。監査記録(実験結果・ログ・全所見)は **リポのファイルに置きパスで参照**する — メッセージは
  記録の射影であって記録ではない。数値には限定子を付ける(機構の性能か・人間や運転員の判断込みか・N・未測定の failure class)。
  人間や運転員の判断で救われた例は機構の成功に数えない。
- INFORM: 分かったこと → 意味・示唆(必要なら)→ `human_action: none` → execution の 1 行(次の一手 / 未実施項目 / 再開条件)。
  **待機形**(ハーネス通知待ちでターンが切れるとき): ヘッダ+「何を待つ・何がそれに依存する」の 1〜2 行のみ。同じ待機が続いても本文を増やさない
  (読み飛ばせることが価値 — v0.2 実測: 67 handoff 中 38 通がこの型で、user は INFORM に注意を割かずに済んだと評価)。
- DECIDE: **decision_question を本文の先頭に置く**(1 文・回答により状態が確定する形。状態報告や経緯は末尾か付録へ — 人間が探すのは質問)。
  options は 2〜4 個を default とし相互排他。**各案を同じ形で並べる**: `得るもの / 失うもの / 戻せるか / 採ると次に何が起きる`(表または同順の 1 行)。
  独立に採否できる項目は 1 案に束ねず番号を分ける(人間が `1:A,A',C` のように部分採択できる形。依存があれば依存順に並べる)。recommendation は
  options の 1 つを名指しし、理由は観測の羅列でなく「何が示せて何が示せないか」+**非推奨案がなぜ劣るか 1 行**。reply_format は人間の返答コストを
  固定する(例: `A` / `1:A 2:B` / `OTHER: 理由` / `MODIFY: 条件`)。
- DISCUSS: discussion_question は範囲が一意に分かる問い(A/B 形に限定しない)。thesis はその問いへの現在の回答 1 文。reasoning は 3 点以内。
  counterpoint は自分の thesis への最強の反論 1 点。what_would_change_thesis を 1 行。末尾に「裁定要求ではない」と、返答の形(`AGREE` /
  `DISAGREE: 理由` / 自由記述)。
- REQUEST: request は 1 段落(何を・どこで・どの手順書で)。deliverable は**穴埋め様式**— 返してほしい行を欄名つきで全部並べ、記入例を 1 行添える。
  人間はそれを埋めて返す(v0.2 実測: 様式なしで台帳を依頼し回収に追加 5 往復)。欄が埋まらずに返ったら再 REQUEST の前に様式の欠陥を疑う。why_human は 1 行
  (例: 「運転員= 人間という実験設計」「私の権限外」「私が触ると測定が汚れる」)。作業の所要目安を添える。
- 付録: 主モード以外の内容を同じメッセージに残す場合は、パケットの後に `---` と `付録(INFORM・返答不要)` の見出しで区切る。
  付録に疑問文・裁定・「〜しますか」を置かない。

### 2.3 検査(validate)— 構造検査と意味自己検査は別計器

```text
structural(lint・機械的に判定できる)
  H1 先頭行が [mode / execution] の形で、語彙内
  H2 組合せが §1 の許容表にある(INFORM/BLOCKED は無効 — 人間の返答を待つなら DECIDE / DISCUSS / REQUEST へ)
  F1 mode の必須要素がすべて存在する(見出し・ラベル・または明瞭な 1 文)
  F2 DECIDE: decision_question が本文先頭にあり、options が各案同形の帰結(得る/失う/戻せるか)つきで列挙され、独立項目は番号が分かれ、reply_format がある
  F3 DISCUSS: discussion_question と thesis が両方ある
  F4 REQUEST: request・deliverable(穴埋め様式・記入例つき)・why_human がある。INFORM に human_action あり(依頼・疑問文)は F1 違反= REQUEST か DECIDE へ再分類
  F5 待機形: ヘッダ+2 行以内
  F6 区間: フリースタイル区間の開始に人間の宣言がある(AI 推定で形式なしにしない)/ 区間内で裁定・依頼・タスク終了を含む通にヘッダと「区間は継続」がある
  M1 付録の外に、宣言外モードの内容(疑問文・裁定・議題・依頼)がない

semantic(self-review・自己申告 — 較正は人間の mode 訂正回数で外から測る)
  P1 メッセージの目的が宣言した mode と一致する(読み手が「私は何をすれば?」と問わずに済むか)
  P2 DECIDE: recommendation が evidence から従い、限定子が主張を実際に絞っている
  P3 DISCUSS: thesis が discussion_question への回答になっている・counterpoint が thesis を実際に脅かす
  P4 execution が本文と矛盾しない(BLOCKED なのに作業継続を書いていない・COMPLETE なのに未実施が隠れていない)
```

### 2.4 書き直し(rewrite)

FAIL があれば送る前に書き直す。default 上限 2 回。**structural(H/F/M)の FAIL は送信停止**— 機械的に直せるものを申告付きで送らない(v0.2 実測:
FAIL H2 を申告しつつ 3 通送り、user の訂正で止まった。申告は検査の代わりにならない)。上限で残る **semantic(P)の FAIL のみ** 末尾に
`self-check: FAIL <id>(理由)` を 1 行で自己申告する(未収束を収束と報告しない — converge と同じ形)。structural / semantic は将来別々に較正できるよう id で区別する。

### 2.5 DISCUSS の収束(default)

同じ discussion_question で 3 往復して thesis が動かないなら、DECIDE に切り替えて人間に確定を求める(裁定点へ写す)。
BLOCKED の DISCUSS に返答がない間、AI は既定の thesis で進んではいけない。

### 2.6 BomDD の停止語彙との対応(参考)

NORMATIVE_RULING / CONVERGENCE_LIMIT → DECIDE/BLOCKED。PREFLIGHT_HOLD → DECIDE/BLOCKED(入力が要る)か INFORM/PAUSED(待つだけ)。
VERIFICATION_FAIL → 是正中なら INFORM/CONTINUING、是正方針が分岐するなら DECIDE。LEDGER_INCONSISTENT → 裁定材料を DECIDE で提示
(原文パス提示・要約しない)。

### 2.7 適用外

ターン途中の進捗の一行(ターンを終えないもの)。**フリースタイル区間**(§1・v0.4): 人間の宣言で開始・終了し、区間内は形式なし。ただし裁定・依頼・タスクの
ターン終了を含む 1 通はその通だけ契約に戻り「区間は継続」と明記する(片方向ラチェット)。AI の推定で区間に入らない(既定は契約)。**ターンを終える待機(バックグラウンド通知待ち)は適用外ではなく
待機形 INFORM/CONTINUING**(v0.3。v0.2 では適用外に見えたが実測では handoff の 57% を占め、ヘッダが読み飛ばしを可能にしていた)。

## 3. 例(最小形)

```text
[INFORM / COMPLETE]
ECO-065 verified(CI 34516211684 success・register verified・窓閉鎖)。詳細= bomdd/60-change-order-eco-065.md §7。
human_action: none。未実施= なし。次の裁定材料は別 handoff で出す。
```

```text
[INFORM / CONTINUING]
self-conformance の exit 観測待ち。以降(witness → commit → push → CI)はすべてこれに依存する。
```

```text
(user: ここからはフリースタイルで)
(形式なしの会話が続く)

[DECIDE / PAUSED]  ← 区間内で裁定が必要になった 1 通だけ契約に戻る
decision_question: …
options: …
reply_format: A / B
execution: PAUSED — 区間は継続(返答後はフリースタイルに戻る)。
```

```text
[DECIDE / BLOCKED]
decision_question: Phase 6(狭い自動起動)を今開くか。
options:
  A 開く         — 得る: 自動起動 job の witness 再検証を次に測れる / 失う: run-02 の切り分け前に機構を積む / 戻せる: 可(順序の入替) / 次: Phase 6 起票
  B run-02 先行  — 得る: operator rescue 依存を切り分けてから開ける / 失う: 1 run 分の時間 / 戻せる: 可 / 次: run-02 ブリーフ
recommendation: B。fail-open 0/7 は運転員+検証器の性能で、2 件は運転員の仕様外行動に依存し、dirty 腕は未測定。A が劣る理由: 未測定の failure class の上に自動起動を積む。
reply_format: A / B / OTHER: 理由
execution: BLOCKED — Phase 6 の作業は回答まで着手しない。
---
付録(INFORM・返答不要): run-01 の記録= bomdd/reports/phase5-run-01-eco-062.md
```

```text
[DISCUSS / PAUSED]
discussion_question: 契約 v0 に「handoff の定義」と「1 パケット 1 主モード」を契約側として足すか。
thesis: 足す。どちらも実装規則でなく通信契約の側の制約。
reasoning: (3 点以内)
counterpoint: 分割でメッセージ数が増える。
what_would_change_thesis: 付録方式で裁定の再分析が起きなければ分割は実装の選択に落とす。
裁定要求ではない。返答: AGREE / DISAGREE: 理由 / 自由記述。
```

```text
[REQUEST / BLOCKED]
request: run-02 の R1〜R8 を bomdd/reports/phase5-run-02-brief.md の手順 v2 で実施してください(所要 20〜30 分)。
deliverable(穴埋め・そのまま返す):
  R1 | decision= | code= | 1 行目=
  …(R8 まで同形)
  R7 issue= / options= / 手順の欠落=(なければ「なし」)
  例: R1 | decision=ADVANCE | code=OK | 1 行目=ADVANCE OK: tree 一致
why_human: 運転員= 人間という実験設計(裁定 A)。私が実行すると運転員≠製造者が崩れる。
execution: BLOCKED — 台帳が届くまで採点・R9 に進まない。
```

## 4. 計測(試行・user 裁定 2026-09-11 2:A)

- 単位: handoff 20 回(うち DECIDE 5 回以上)で評価。EXP-20260911-01(improvements.md)。
- 指標: ①人間が mode を訂正した回数 ②「で、私は何をすれば」型の再質問回数 ③DECIDE への返答が reply_format どおり 1 語(またはラベル列)で済んだ比率。
- 基準線(契約前・Phase 5 run-01 報告): 訂正 1・再分析 1・1 語返答 0/1。
- 試行中の記録(契約後): 2026-09-11 mode 訂正 1(run-02 依頼を INFORM で送信・self-check FAIL H2 を申告しつつ送った → user 訂正 → v0.2 REQUEST 追加)。
- 評価後の分岐: 指標が改善しなければ §2 の細則の一部を §1 へ昇格させて再試行。改善すれば product-profile への正本化を ECO で判断する。
- **評価(2026-09-12・EXP-20260911-01 回収・ECO-070 §0)**: 本セッション transcript 実測 handoff 67(INFORM 44 / DECIDE 12 / REQUEST 8 / DISCUSS 3)。
  ①mode 訂正 1 ②再分析型の再質問 0(運用前の同セッションでは 3)③DECIDE 返答が reply_format どおり 12/12。user 評価: INFORM に注意を割かずに済む・
  DECIDE の温度差が伝わる・根拠(得失)はもっと分かりやすくできる。欠陥: INFORM/BLOCKED を FAIL 申告のまま 3 通送信 / REQUEST 回収に追加 5 往復 /
  DECIDE の冒頭が報告 / option の束ねが粗い。同一セッション・同一 user・N 小で学習効果と未分離(示唆止まり)。→ user 裁定 A= 採用・v0.3。
- **v0.3 の計測(EXP-20260912-01)**: 次の handoff 20 回(DECIDE 5 回以上)で ①許容表外ヘッダ 0 ②structural FAIL 申告つき送信 0 ③REQUEST の成果物回収に
  要した追加往復(v0.2 基準線 5)④DECIDE で人間が非推奨案の理由や部分採択の可否を再質問した回数 ⑤待機形の本文 2 行以内の比率。
  v0.4(ECO-071)追加: ⑥人間の「形式なし」宣言回数(数回を超えれば既定を再検討)⑦区間内で契約に戻った通数と隠れ裁定(戻らず「〜しますか」で終えた)件数= 0 要求
  ⑧AI の推定で形式を落とした件数= 0 要求。thesis を変える条件(DISCUSS 2026-09-12): ⑥が多い/推定が全件正しかった → 既定を AI 推定へ / ⑦>0 → ラチェットを維持・強化。
